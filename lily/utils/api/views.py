import redis
from django.contrib.messages import get_messages
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from lily.accounts.models import Account
from lily.contacts.models import Contact

from .serializers import AddressSerializer
from ..models.models import Address


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
            Q(phone_numbers__number__endswith=phone_number_end)
        ).filter(is_deleted=False).first()

        if contact:
            name = contact.full_name
        else:
            account = Account.objects.filter(
                Q(phone_numbers__number__endswith=phone_number_end)
            ).filter(is_deleted=False).first()

            if account:
                name = account.name
            else:
                name += caller_name

        return HttpResponse('status=ACK&callername=%s' % name, content_type='application/x-www-form-urlencoded')


class CountryViewSet(ModelViewSet):
    """
    List all countries for a tenant.
    """
    queryset = Address.objects
    allowed_methods = ['OPTIONS', 'POST']
    serializer_class = AddressSerializer

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(CountryViewSet, self).get_queryset().all()

    def create(self, request, *args, **kwargs):
        raise exceptions.PermissionDenied


class AppHash(APIView):
    def get(self, request, format=None, *args, **kwargs):
        r = redis.StrictRedis(host=settings.REDIS.hostname, port=settings.REDIS.port, password=settings.REDIS.password)

        app_hash = r.get('app_hash')

        return Response({'app_hash': app_hash})
