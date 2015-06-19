import requests

from django.conf import settings
from django.contrib.messages import get_messages
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import exceptions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.tags.models import Tag

from .serializers import AddressSerializer, EmailAddressSerializer, PhoneNumberSerializer, TagSerializer
from ..models.models import Address, EmailAddress, PhoneNumber


class Queues(APIView):
    """
    List all cases for a tenant.
    """

    def get(self, request, format=None, *args, **kwargs):
        if not request.user.is_superuser:
            raise exceptions.AuthenticationFailed('No permission')

        if not settings.IRONMQ_URL or not settings.IRONMQ_OAUTH:
            raise exceptions.AuthenticationFailed('No permission')

        url = '%s/queues/%s?oauth=%s' % (settings.IRONMQ_URL, kwargs['queue'], settings.IRONMQ_OAUTH)

        resp = requests.get(url)
        queue_info = resp.json()

        if resp.status_code == 200:
            return Response({
                'total_messages': queue_info['total_messages'],
                'size': queue_info['size'],
                'name': queue_info['name'],
            })
        else:
            return exceptions.NotAcceptable


class Notifications(APIView):
    """
    List all notifications posted in request.messages
    """

    def get(self, request, format=None, *args, **kwargs):
        storage = get_messages(request)
        notifications = []

        for message in storage:
            notifications.append({
                'level': message.level_tag,
                'message': message.message,
            })

        return Response(notifications)


class CallerName(APIView):
    """
    Serve a caller name to voipgrid based on the phone number provided
    """

    def get(self, request, format=None, *args, **kwargs):
        name = '[NK]'
        phone_number = request.GET.get('phonenumber', '')
        caller_name = request.GET.get('callername', '')

        if not phone_number:
            return HttpResponse()

        phone_number_end = phone_number[-9:]

        contact = Contact.objects.filter(
            Q(phone_numbers__raw_input__endswith=phone_number_end) | Q(phone_numbers__number__endswith=phone_number_end)
        ).filter(is_deleted=False).first()

        if contact:
            name = contact.full_name()
        else:
            account = Account.objects.filter(
                Q(phone_numbers__raw_input__endswith=phone_number_end) | Q(phone_numbers__number__endswith=phone_number_end)
            ).filter(is_deleted=False).first()

            if account:
                name = account.name
            else:
                name += caller_name

        return HttpResponse('status=ACK&callername=%s' % name, content_type='application/x-www-form-urlencoded')


class RelatedModelViewSet(viewsets.ModelViewSet):

    related_model = None

    def list(self, request, object_pk=None):
        queryset = self._get_related_queryset(object_pk).all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, object_pk=None):
        queryset = self._get_related_queryset(object_pk).filter(pk=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, object_pk=None):
        serializer = self.get_serializer(data=request.data, related_object=self._get_related_object(object_pk))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def _get_related_object(self, object_pk):
        return self.related_model.objects.get(pk=object_pk)

    def _get_related_queryset(self, object_pk):
        pass


class PhoneNumberViewSet(RelatedModelViewSet):
    queryset = PhoneNumber.objects
    serializer_class = PhoneNumberSerializer

    def _get_related_queryset(self, object_pk):
        return self._get_related_object(object_pk).phone_numbers


class EmailAddressViewSet(RelatedModelViewSet):
    queryset = EmailAddress.objects
    serializer_class = EmailAddressSerializer

    def _get_related_queryset(self, object_pk):
        return self._get_related_object(object_pk).email_addresses


class AddressViewSet(RelatedModelViewSet):
    queryset = Address.objects
    serializer_class = AddressSerializer

    def _get_related_queryset(self, object_pk):
        return self._get_related_object(object_pk).addresses


class TagViewSet(RelatedModelViewSet):
    queryset = Tag.objects
    serializer_class = TagSerializer
    related_model = None

    def _get_related_queryset(self, object_pk):
        return self._get_related_object(object_pk).tags

