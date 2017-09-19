import anyjson
import urllib
from datetime import datetime, timedelta

from django.contrib import messages
from django.db import transaction, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.utils.translation import ugettext_lazy as _
from oauth2client.contrib.django_orm import Storage
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from lily.api.drf_extensions.authentication import PandaDocSignatureAuthentication
from lily.contacts.models import Contact
from lily.deals.models import Deal, DealStatus, DealNextStep
from lily.notes.models import Note
from lily.utils.functions import send_get_request
from lily.utils.api.permissions import IsAccountAdmin, IsFeatureAvailable

from .serializers import DocumentSerializer, DocumentEventSerializer
from ..credentials import get_access_token, get_credentials, put_credentials, LilyOAuthCredentials
from ..models import Document, IntegrationCredentials, IntegrationDetails, IntegrationType, DocumentEvent
from ..tasks import import_moneybird_contacts


class DocumentDetails(APIView):
    serializer = DocumentSerializer
    parser_classes = (JSONParser, FormParser)

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
    permission_classes = (IsFeatureAvailable, )
    serializer = DocumentSerializer
    parser_classes = (JSONParser, FormParser)

    def get(self, request, contact_id, format=None):
        """
        List all PandaDoc documents.
        """
        documents = Document.objects.filter(contact=self.kwargs['contact_id'])
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

    def post(self, request, contact_id):
        contact = Contact.objects.get(pk=contact_id)

        deal = Deal.objects.get(pk=request.POST.get('deal_id'))
        document_id = request.POST.get('document_id')

        document = Document.objects.create(contact=contact, deal=deal, document_id=document_id)
        document = DocumentSerializer(document).data

        return Response({'document': document})


class DocumentEventList(APIView):
    permission_classes = (IsFeatureAvailable, )
    model = DocumentEvent
    serializer_class = DocumentEventSerializer

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
                    try:
                        DocumentEvent.objects.exists(event_type=event_type, document_status=document_status)
                    except:
                        pass
                    else:
                        return HttpResponseBadRequest(anyjson.serialize(duplicate_error))

                data = {
                    'event_type': event_type,
                    'document_status': document_status,
                    'add_note': event.get('add_note', False),
                    'extra_days': event.get('extra_days', 0),
                }

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
            deal.next_step_date = deal.next_step_date + timedelta(days=event.extra_days)

        if event.add_note:
            document_name = data.get('name')
            status_name = document_status.replace('document.', '')
            date = datetime.now().strftime('%d/%m/%y %H:%M')

            # Create a note based on the document status.
            content = _('%s was %s on %s') % (document_name, status_name, date)

            note = Note.objects.create(
                content=content,
                content_type=deal.content_type,
                object_id=deal.id,
                author=request.user,
            )

            deal.notes.add(note)

        deal.save()

        return Response(status=status.HTTP_200_OK)


class PandaDocSharedKey(APIView):
    permission_classes = (IsAccountAdmin, IsFeatureAvailable)

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
    permission_classes = (IsAccountAdmin, IsFeatureAvailable)

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
    permission_classes = (IsAccountAdmin, IsFeatureAvailable)

    def post(self, request, integration_type):
        """
        Get the authentication URL for the given integration type.
        """
        client_id = request.POST.get('client_id')
        client_secret = request.POST.get('client_secret')
        integration_context = request.POST.get('integration_context')

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

        if error:
            messages.error(
                self.request._request,  # add_message needs an HttpRequest object
                _('Sorry, Please authorize Lily to use the integration.')
            )

            return HttpResponseRedirect('/#/preferences/admin/integrations/%s' % integration_type)

        credentials = get_credentials(integration_type)

        if not credentials:
            response = anyjson.serialize({'error': 'No credentials found. Please enter your credentials again'})
            return HttpResponse(response, content_type='application/json')

        get_access_token(credentials, integration_type, code)

        messages.success(
            self.request._request,  # add_message needs an HttpRequest object
            _('Your credentials have been saved.')
        )

        return HttpResponseRedirect('/#/preferences/admin/integrations')
