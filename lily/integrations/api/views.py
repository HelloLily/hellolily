import anyjson
import urllib

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.utils.translation import ugettext_lazy as _
from oauth2client.contrib.django_orm import Storage
from rest_framework.parsers import FormParser
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from lily.contacts.models import Contact
from lily.deals.models import Deal
from lily.utils.functions import send_get_request
from lily.utils.api.permissions import IsAccountAdmin, IsFeatureAvailable

from .serializers import DocumentSerializer
from ..credentials import get_access_token, get_credentials, put_credentials, LilyOAuthCredentials
from ..models import Document, IntegrationCredentials, IntegrationDetails, IntegrationType
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
