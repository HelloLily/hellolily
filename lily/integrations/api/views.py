import anyjson
import datetime
import logging
import re
import requests
import time
import urllib
from hashlib import sha256

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.utils.translation import ugettext_lazy as _
from django.utils.text import Truncator
from django.core.exceptions import ObjectDoesNotExist

from oauth2client.contrib.django_orm import Storage
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from lily.api.drf_extensions.authentication import PandaDocSignatureAuthentication
from lily.contacts.models import Contact
from lily.deals.models import Deal, DealStatus, DealNextStep
from lily.notes.models import Note
from lily.utils.functions import send_get_request
from lily.utils.models.models import EmailAddress
from lily.utils.api.permissions import IsAccountAdmin, IsFeatureAvailable

from .serializers import DocumentSerializer, DocumentEventSerializer
from ..credentials import get_access_token, get_credentials, put_credentials, LilyOAuthCredentials
from ..models import Document, IntegrationCredentials, IntegrationDetails, SlackDetails, IntegrationType, DocumentEvent
from ..tasks import import_moneybird_contacts


logger = logging.getLogger(__name__)


class DocumentDetails(APIView):
    serializer = DocumentSerializer
    parser_classes = (JSONParser, FormParser)
    swagger_schema = None

    def get(self, request, document_id, format=None):
        """
        Get details of the given document.
        """
        document = {}

        try:
            document = Document.objects.get(document_id=self.kwargs['document_id'])
        except Document.DoesNotExist:
            pass
        else:
            deal = Deal.objects.get(pk=document.deal_id)
            document = DocumentSerializer(document).data
            document.update({
                'deal': {
                    'id': deal.id,
                    'status': deal.status_id,
                    'modified': deal.modified,
                },
                'assigned_to': {
                    'id': deal.assigned_to.id,
                    'full_name': deal.assigned_to.full_name,
                } if deal.assigned_to else None,
            })

        return Response({'document': document})


class PandaDocList(APIView):
    permission_classes = (IsAuthenticated, IsFeatureAvailable, )
    serializer = DocumentSerializer
    parser_classes = (JSONParser, FormParser)
    swagger_schema = None

    def get(self, request, deal_id, format=None):
        """
        List all PandaDoc documents.
        """
        documents = Document.objects.filter(deal_id=deal_id)
        temp_documents = []

        credentials = get_credentials('pandadoc')

        for document in documents:
            url = 'https://api.pandadoc.com/public/v1/documents/%s/details' % document.document_id

            response = send_get_request(url, credentials)

            data = response.json()

            if data.get('id'):
                temp_documents.append(data)
            else:
                # No details could be retreived, so it's probably been deleted in PandaDoc.
                document.delete()

        return Response({'documents': temp_documents})

    def post(self, request, deal_id):
        contact = Contact.objects.get(pk=request.POST.get('contact_id'))

        deal = Deal.objects.get(pk=deal_id)
        document_id = request.POST.get('document_id')

        document = Document.objects.create(contact=contact, deal=deal, document_id=document_id)
        document = DocumentSerializer(document).data

        return Response({'document': document})


class DocumentEventList(APIView):
    permission_classes = (IsAuthenticated, IsFeatureAvailable, )
    model = DocumentEvent
    serializer_class = DocumentEventSerializer
    swagger_schema = None

    def get(self, request, format=None):
        events = DocumentEvent.objects.all().order_by('id')
        events = DocumentEventSerializer(events, many=True).data

        return Response({'results': events})

    def post(self, request):
        event_data = request.data

        duplicate_error = {
            'duplicate_event': 'Only one event per type allowed'
        }

        events = []

        for event in event_data:
            event_id = event.get('id')

            if not event.get('is_deleted'):
                event_type = event.get('event_type')
                document_status = event.get('document_status')

                if not event_id:
                    # New object so check if event with given parameters already exists.
                    if DocumentEvent.objects.exists(event_type=event_type, document_status=document_status):
                        return HttpResponseBadRequest(anyjson.serialize(duplicate_error))

                data = {
                    'event_type': event_type,
                    'document_status': document_status,
                    'add_note': event.get('add_note', False),
                    'extra_days': event.get('extra_days', 0),
                }

                if not data.get('extra_days'):
                    data.update({
                        'set_to_today': event.get('set_to_today', False)
                    })

                event_id = event.get('id')

                deal_status = event.get('status')

                if deal_status:
                    deal_status = DealStatus.objects.get(pk=deal_status)

                data.update({'status': deal_status})

                next_step = event.get('next_step')

                if next_step:
                    next_step = DealNextStep.objects.get(pk=next_step)

                data.update({'next_step': next_step})

                events.append({'id': event_id, 'data': data})
            else:
                events.append({'id': event_id, 'is_deleted': True})

        try:
            with transaction.atomic():
                for event in events:
                    if not event.get('is_deleted'):
                        DocumentEvent.objects.update_or_create(id=event.get('id'), defaults=event.get('data'))
                    else:
                        if event.get('id'):
                            DocumentEvent.objects.get(pk=event.get('id')).delete()
        except IntegrityError:
            return HttpResponseBadRequest(anyjson.serialize(duplicate_error))

        return Response(status=status.HTTP_201_CREATED)


class DocumentEventCatch(APIView):
    authentication_classes = (PandaDocSignatureAuthentication, )
    swagger_schema = None

    def post(self, request):
        data = request.data[0].get('data')
        event = request.data[0].get('event')
        document_status = data.get('status')

        try:
            event = DocumentEvent.objects.get(event_type=event, document_status=document_status)
        except DocumentEvent.DoesNotExist:
            # No event set with given event type, so just return 404.
            return Response(status=status.HTTP_404_NOT_FOUND)

        deal = Deal.objects.get(pk=data.get('metadata').get('deal'))

        # Set deal values if the webhook has specified them.
        if event.status:
            deal.status = event.status

        if event.next_step:
            deal.next_step = event.next_step

        if event.extra_days:
            deal.next_step_date = deal.next_step_date + datetime.timedelta(days=event.extra_days)
        elif event.set_to_today:
            deal.next_step_date = datetime.date.today()

        if event.add_note:
            document_name = data.get('name')
            status_name = document_status.replace('document.', '')
            date = datetime.datetime.now().strftime('%d/%m/%y %H:%M')

            # Create a note based on the document status.
            content = _('%s was %s on %s') % (document_name, status_name, date)

            note = Note.objects.create(
                content=content,
                gfk_content_type=deal.content_type,
                gfk_object_id=deal.id,
                author=request.user,
            )

            deal.notes.add(note)

        deal.save()

        return Response(status=status.HTTP_200_OK)


class PandaDocSharedKey(APIView):
    permission_classes = (IsAuthenticated, IsAccountAdmin, IsFeatureAvailable)
    swagger_schema = None

    def get(self, request):
        """
        Get the authentication URL for the given integration type.
        """
        credentials = get_credentials('pandadoc')

        shared_key = credentials.integration_context.get('shared_key')

        return Response({'shared_key': shared_key}, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Get the authentication URL for the given integration type.
        """
        shared_key = request.data.get('shared_key')

        credentials = get_credentials('pandadoc')

        credentials.integration_context.update({
            'shared_key': shared_key,
        })

        put_credentials('pandadoc', credentials)

        return Response(status=status.HTTP_200_OK)


class MoneybirdContactImport(APIView):
    permission_classes = (IsAuthenticated, IsAccountAdmin, IsFeatureAvailable)
    swagger_schema = None

    def post(self, request):
        credentials = get_credentials('moneybird')

        if not credentials:
            errors = {
                'no_credentials': [_('No Moneybird credentials found')]
            }
            return HttpResponseBadRequest(anyjson.serialize(errors), content_type='application/json')

        credentials.integration_context.update({
            'auto_sync': self.request.data.get('auto_sync'),
        })

        put_credentials('moneybird', credentials)

        import_moneybird_contacts.apply_async(args=(self.request.user.tenant.id,))

        return Response({'import_started': True})


class EstimatesList(APIView):
    swagger_schema = None

    def get(self, request, contact_id, format=None):
        """
        List all Moneybird estimates.
        """
        credentials = get_credentials('moneybird')

        url = 'https://moneybird.com/api/v2/%s/estimates' % credentials.integration_context.get('administration_id')

        response = send_get_request(url, credentials)

        data = response.json()

        return Response({'estimates': data})


class IntegrationAuth(APIView):
    parser_classes = (JSONParser, FormParser)
    permission_classes = (IsAuthenticated, IsAccountAdmin, IsFeatureAvailable)
    swagger_schema = None

    def post(self, request, integration_type):
        """
        Get the authentication URL for the given integration type.
        """
        is_slack = integration_type == 'slack'

        if is_slack:
            client_id = settings.SLACK_LILY_CLIENT_ID
            client_secret = settings.SLACK_LILY_CLIENT_SECRET
        else:
            client_id = request.POST.get('client_id')
            client_secret = request.POST.get('client_secret')

        integration_context = request.POST.get('integration_context', {})

        if integration_context:
            integration_context = anyjson.loads(integration_context)

        errors = {}

        if not client_id:
            errors.update({
                'client_id': ['Please enter a valid client ID'],
            })

        if not client_secret:
            errors.update({
                'client_secret': ['Please enter a valid client secret'],
            })

        if errors:
            return HttpResponseBadRequest(anyjson.serialize(errors), content_type='application/json')

        integration_type = IntegrationType.objects.get(name__iexact=integration_type)
        redirect_uri = request.build_absolute_uri()

        params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'scope': integration_type.scope,
            'response_type': 'code',
        }

        if is_slack:
            # Save a unique identifier so we can verify the follow up request from Slack is legit.
            state = sha256('%s-%s' % (
                self.request.user.id,
                settings.SECRET_KEY
            )).hexdigest()

            params.update({'state': state})

            details, created = SlackDetails.objects.get_or_create(type=integration_type)
        else:
            details, created = IntegrationDetails.objects.get_or_create(type=integration_type)

        storage = Storage(IntegrationCredentials, 'details', details, 'credentials')

        credentials = LilyOAuthCredentials(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            integration_context=integration_context,
        )

        storage.put(credentials)

        auth_url = integration_type.auth_url + urllib.urlencode(params)

        response = anyjson.serialize({'url': auth_url})

        return HttpResponse(response, content_type='application/json')

    def get(self, request, integration_type, format=None):
        """
        Exchange a authorization code for an access token for the given integration type.
        """
        code = str(request.GET.get('code'))
        error = request.GET.get('error')
        is_slack = integration_type == 'slack'

        if error:
            messages.error(
                self.request._request,  # add_message needs an HttpRequest object
                _('Sorry, Please authorize Lily to use the integration.')
            )

            return HttpResponseRedirect('/#/preferences/admin/integrations/%s' % integration_type)

        if is_slack:
            state = request.GET.get('state')

            generated_state = sha256('%s-%s' % (
                self.request.user.id,
                settings.SECRET_KEY
            )).hexdigest()

            if state != generated_state:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        credentials = get_credentials(integration_type)

        if not credentials:
            response = anyjson.serialize({'error': 'No credentials found. Please enter your credentials again'})
            return HttpResponse(response, content_type='application/json')

        get_access_token(credentials, integration_type, code)

        if is_slack:
            message = _('Lily Slack app has been installed successfully.')
        else:
            message = _('Your credentials have been saved.')

        messages.success(
            self.request._request,  # add_message needs an HttpRequest object
            message,
        )

        return HttpResponseRedirect('/#/preferences/admin/integrations')


class IntegrationDetailsView(APIView):
    swagger_schema = None

    def get(self, request, integration_type, format=None):
        credentials = get_credentials(integration_type)

        # If no credentials exist then the given integration isn't installed.
        has_integration = credentials is not None

        details = {
            'has_integration': has_integration
        }

        if has_integration:
            details.update({
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'integration_context': credentials.integration_context,
            })

        response = anyjson.serialize(details)

        return HttpResponse(response, content_type='application/json')

    def delete(self, request, integration_type):
        credentials = get_credentials(integration_type)

        if credentials:
            try:
                integration_type = IntegrationType.objects.get(name__iexact=integration_type)
            except IntegrationType.DoesNotExist:
                pass
            else:
                details = IntegrationDetails.objects.get(type=integration_type)
                details.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class SlackEventCatch(APIView):
    authentication_classes = []
    permission_classes = []
    swagger_schema = None

    def convert_to_string(self, data):
        """
        Slack doesn't like unicode. So we want to loop through all the data
        and convert to string if needed.
        """
        for key in data:
            value = data[key]

            if isinstance(value, list):
                # Value is a list, so check all its items and recursivly convert to string.
                for item in value:
                    item = self.convert_to_string(item)

                data[key] = value
            elif isinstance(value, dict):
                # Value is a dict, so we want to convert all its values to string.
                data[key] = self.convert_to_string(value)
            else:
                try:
                    data[key] = str(value)
                except UnicodeEncodeError:
                    # Converting to a readable character seems to very hard,
                    # so just ignore special characters.
                    data[key] = str(value.encode('ascii', 'ignore').decode('ascii'))

        return data

    def format_slack_date(self, date):
        """
        Convert the given date object to a string which Slack accepts.
        """
        date_format = '%b. %d %Y'
        timestamp = int(time.mktime(date.timetuple()))
        fallback = date.strftime(date_format)

        date = '<!date^%s^{date_short}|%s>' % (timestamp, fallback)

        return date

    def get_author_name(self, obj):
        author_name = ''

        if obj.contact:
            author_name += obj.contact.full_name

        if obj.contact and obj.account:
            author_name += ' at '

        if obj.account:
            author_name += obj.account.name

        return author_name

    def get_data(self, url, details):
        data = {}
        extra_data = {}
        # Check if unfurling is supported for the given URL.
        matches = re.search('((case|deal|account|contact)(?:s))\/(\d+)', url)

        if matches:
            app_label = matches.group(1)
            model = matches.group(2)
            obj_id = matches.group(3)

            content_type = ContentType.objects.get(app_label=app_label, model=model)

            try:
                obj = content_type.get_object_for_this_type(pk=obj_id, tenant=details.tenant)
            except (ObjectDoesNotExist, ValueError):
                return None

            fields = []

            if model == 'case' or model == 'deal':
                extra_data = {
                    'author_name': self.get_author_name(obj),
                    'text': Truncator(obj.description).chars(250),
                    'ts': int(time.mktime(obj.created.timetuple()))
                }
            if model == 'account' or model == 'contact':
                email_addresses = obj.email_addresses.exclude(status=EmailAddress.INACTIVE_STATUS)
                email_string = '\n'.join([email.email_address for email in email_addresses])

                phone_numbers = obj.phone_numbers.all()
                phone_string = '\n'.join([phone.number for phone in phone_numbers])

                fields = [
                    {
                        'title': _('Email addresses'),
                        'value': email_string or 'None',
                        'short': True
                    },
                    {
                        'title': _('Phone numbers'),
                        'value': phone_string or 'None',
                        'short': True
                    },
                ]

            if model == 'case':
                title = obj.subject

                fields = [
                    {
                        'title': _('Priority & type'),
                        'value': '%s, %s' % (obj.get_priority_display(), obj.type.name),
                        'short': True
                    },
                    {
                        'title': _('Status'),
                        'value': obj.status.name,
                        'short': True
                    },
                    {
                        'title': _('Expiry date'),
                        'value': self.format_slack_date(obj.expires),
                        'short': True
                    }
                ]

                COLORS = ['#a0e0d4', '#97d5fc', '#ffd191', '#ff7097']

                extra_data.update({'color': COLORS[obj.priority]})
            elif model == 'deal':
                title = obj.name

                fields = [
                    {
                        'title': _('Status'),
                        'value': obj.status.name,
                        'short': True
                    },
                    {
                        'title': _('Next step'),
                        'value': obj.next_step.name,
                        'short': True
                    },
                    {
                        'title': _('Next step date'),
                        'value': self.format_slack_date(obj.next_step_date),
                        'short': True
                    },
                    {
                        'title': _('One-time costs'),
                        'value': obj.amount_once,
                        'short': True
                    },
                    {
                        'title': _('Recurring costs'),
                        'value': obj.amount_recurring,
                        'short': True
                    },
                ]
            elif model == 'account':
                title = obj.name
            elif model == 'contact':
                title = obj.full_name

                account_string = ''

                for function in obj.functions.all():
                    account_string += function.account.name

                    if not function.is_active:
                        account_string += ' (inactive)'

                    account_string += '\n'

                fields.append({
                    'title': _('Works at'),
                    'value': account_string,
                    'short': True
                })

            if model != 'contact':
                fields.append({
                    'title': _('Assigned to'),
                    'value': obj.assigned_to.full_name if obj.assigned_to else 'Nobody',
                    'short': True,
                })

        data = {
            'fallback': 'Lily - %s details' % model.title(),
            'title': title,
            'title_link': url,
            'color': '#9f5edc',
            'fields': fields,
            'footer': 'Lily',
            'footer_icon': 'https://app.hellolily.com/favicon.ico',
        }

        data.update(extra_data)

        data = self.convert_to_string(data)

        return data

    def post(self, request):
        data = request.data
        team_id = data.get('team_id')
        event = data.get('event')

        if data.get('token') != settings.SLACK_LILY_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # The type of the verification event isn't in the event object.
        if data.get('type') == 'url_verification':
            return Response({'challenge': data.get('challenge')}, status=status.HTTP_200_OK)

        if not team_id:
            # Not url verification, so we require the team ID.
            return Response(status=status.HTTP_403_FORBIDDEN)

        # If we were to use the type given in the data we'd have an event_callback
        # for the following events.
        # So retrieve the actual type from the 'event' object.
        event_type = event.get('type')

        details = SlackDetails.objects.filter(team_id=team_id).first()

        # Slack sends the app_uninstalled event twice.
        if event_type == 'app_uninstalled' and details:
            details.delete()
            details = None

        if details:
            if event_type == 'link_shared':
                unfurls = {}

                for link in event.get('links'):
                    # Convert to string so we can use it later.
                    url = str(link.get('url'))

                    data = self.get_data(url, details)

                    if data:
                        unfurls.update({url: data})

                if unfurls:
                    credentials = get_credentials('slack', details.tenant)

                    data = {
                        'token': credentials.access_token,
                        'channel': event.get('channel'),
                        'ts': event.get('message_ts'),
                        'unfurls': unfurls,
                    }

                    request = requests.post('https://slack.com/api/chat.unfurl?' + urllib.urlencode(data))

                    return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)
