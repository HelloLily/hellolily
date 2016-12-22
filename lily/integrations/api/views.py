import anyjson
import urllib

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.utils.translation import ugettext_lazy as _
from oauth2client.contrib.django_orm import Storage
from rest_framework.views import APIView
from rest_framework.response import Response

from lily.contacts.models import Contact
from lily.deals.models import Deal
from lily.utils.functions import send_get_request

from .serializers import DocumentSerializer
from ..credentials import authenticate_pandadoc, get_credentials, LilyOAuthCredentials
from ..models import IntegrationCredentials, IntegrationDetails, Document


class DocumentDetails(APIView):
    serializer = DocumentSerializer
    """
    List all PandaDoc documents.
    """
    def get(self, request, document_id, format=None):
        document = {}

        try:
            document = Document.objects.get(document_id=self.kwargs['document_id'])
        except Document.DoesNotExist:
            pass
        else:
            document = DocumentSerializer(document).data

        return Response({'document': document})


class PandaDocList(APIView):
    serializer = DocumentSerializer
    """
    List all PandaDoc documents.
    """
    def get(self, request, contact_id, format=None):
        documents = Document.objects.filter(contact=self.kwargs['contact_id'])
        temp_documents = []

        credentials = get_credentials(IntegrationDetails.PANDADOC)

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


class PandaDocAuth(APIView):
    def post(self, request):
        client_id = request.POST.get('client_id')
        client_secret = request.POST.get('client_secret')

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

        params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': request.build_absolute_uri(),
            'scope': 'read+write',
            'response_type': 'code',
        }

        details, created = IntegrationDetails.objects.get_or_create(type=IntegrationDetails.PANDADOC)

        storage = Storage(IntegrationCredentials, 'details', details, 'credentials')

        credentials = storage.get()

        if not credentials:
            credentials = LilyOAuthCredentials(
                client_id=client_id,
                client_secret=client_secret,
            )

        storage.put(credentials)

        auth_url = 'https://app.pandadoc.com/oauth2/authorize?' + urllib.urlencode(params)

        response = anyjson.serialize({'url': auth_url})

        return HttpResponse(response, content_type='application/json')

    def get(self, request, format=None):
        code = str(request.GET.get('code'))
        error = request.GET.get('error')

        if error:
            messages.error(
                self.request._request,  # add_message needs an HttpRequest object
                _('Sorry, Lily needs authorization from PandaDoc to use it.')
            )

            return HttpResponseRedirect('/#/preferences/admin/integrations/pandadoc')

        credentials = get_credentials(IntegrationDetails.PANDADOC)

        if not credentials:
            response = anyjson.serialize({'error': 'No credentials found. Please enter your credentials again'})
            return HttpResponse(response, content_type='application/json')

        authenticate_pandadoc(credentials, IntegrationDetails.PANDADOC, code)

        messages.success(
            self.request._request,  # add_message needs an HttpRequest object
            _('Your PandaDoc credentials have been saved.')
        )

        return HttpResponseRedirect('/#/preferences/admin/integrations')
