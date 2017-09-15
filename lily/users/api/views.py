from datetime import date
from hashlib import sha256

from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse_lazy
from django.core.validators import validate_email
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from django_otp import devices_for_user
from django_otp.plugins.otp_static.models import StaticToken
from rest_framework import mixins, viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser
from two_factor.models import PhoneDevice
from two_factor.templatetags.two_factor import mask_phone_number, format_phone_number
from two_factor.utils import default_device, backup_phones
from user_sessions.models import Session
from templated_email import send_templated_mail

from lily.utils.functions import post_intercom_event

from lily.utils.functions import has_required_tier

from .utils import get_info_text_for_device
from .serializers import (TeamSerializer, LilyUserSerializer, LilyUserTokenSerializer, SessionSerializer,
                          UserInviteSerializer)
from ..models import Team, LilyUser, UserInfo, UserInvite


class TeamFilter(FilterSet):
    """
    Class to filter case queryset.
    """

    class Meta:
        model = Team
        fields = ['name', ]


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List all teams assigned to the current user.
    """
    model = Team
    serializer_class = TeamSerializer
    filter_class = TeamFilter
    queryset = Team.objects

    def get_queryset(self):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id)
        return queryset

    @list_route(methods=['GET'])
    def mine(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(user=self.request.user)
        filtered_queryset = self.filter_class(request.GET, queryset=queryset).qs
        serializer = self.serializer_class(filtered_queryset, context={'request': request}, many=True)
        return Response(serializer.data)


class UserInviteViewSet(viewsets.ModelViewSet):
    model = UserInvite
    serializer_class = UserInviteSerializer
    queryset = UserInvite.objects

    def get_queryset(self):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id)
        return queryset

    def create(self, request):
        protocol = self.request.is_secure() and 'https' or 'http'
        date_string = date.today().strftime('%d%m%Y')
        tenant_id = self.request.user.tenant_id

        # Get the current site or empty string.
        try:
            current_site = Site.objects.get_current()
        except Site.DoesNotExist:
            current_site = ''

        invites = request.data.get('invites')
        errors = []

        for invite in invites:
            first_name = invite.get('first_name')
            email = invite.get('email')
            valid_email = True

            try:
                validate_email(email)
            except:
                valid_email = False

            if not first_name or not email or not valid_email:
                errors.append({
                    'name': [_('Please enter a first name and valid email address')],
                })

            if UserInvite.objects.filter(email=email).exists():
                errors.append({
                    'name': [_('An invite has already been sent to this email address')],
                })

            if LilyUser.objects.filter(email=email, is_active=True).exists():
                errors.append({
                    'name': [_('An user with this email address already exists')],
                })

        if errors:
            return Response({'invites': errors}, status=status.HTTP_400_BAD_REQUEST)

        for invite in invites:
            first_name = invite.get('first_name')
            email = invite.get('email')

            params = {
                'first_name': first_name,
                'email': email,
            }

            invite = UserInvite.objects.filter(**params).first()
            # An invite was already sent, so delete the old one.
            if invite:
                invite.delete()

            # We always want to create a new invite.
            invite = UserInvite.objects.create(**params)

            hash = sha256('%s-%s-%s-%s-%s' % (
                tenant_id,
                invite.id,
                email,
                date_string,
                settings.SECRET_KEY
            )).hexdigest()
            invite_link = '%s://%s%s' % (protocol, current_site, reverse_lazy('invitation_accept', kwargs={
                'tenant_id': tenant_id,
                'first_name': first_name,
                'email': email,
                'date': date_string,
                'hash': hash,
            }))

            # Email to the user.
            send_templated_mail(
                template_name='invitation',
                recipient_list=[email],
                context={
                    'current_site': current_site,
                    'inviter_full_name': self.request.user.full_name,
                    'inviter_first_name': self.request.user.first_name,
                    'recipient_first_name': first_name,
                    'invite_link': invite_link,
                },
                from_email=settings.EMAIL_PERSONAL_HOST_USER,
                auth_user=settings.EMAIL_PERSONAL_HOST_USER,
                auth_password=settings.EMAIL_PERSONAL_HOST_PASSWORD
            )

        if len(invites):
            post_intercom_event(event_name='invite-sent', user_id=self.request.user.id)

            return Response(status=status.HTTP_200_OK)


class LilyUserFilter(FilterSet):
    class Meta:
        model = LilyUser
        fields = {
            'is_active': ['exact', ],
            'teams': ['isnull', ],
        }


class LilyUserViewSet(viewsets.ModelViewSet):
    """
    Returns a list of all users in the system, filtered by default on active status.

    #Ordering#
    Ordering is enabled on this API.

    To order, provide a comma separated list to the ordering argument. Use `-` minus to inverse the ordering.

    #Filtering#
    Filtering is enabled on this API.

    To filter, provide a field name to filter on followed by the value you want to filter on.

    #Examples#
    - plain: `/api/users/`
    - order: `/api/users/?ordering=first_name,-id`
    - filter: `/api/users/?is_active=True`

    #Returns#
    * List of cases with related fields
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = LilyUser.objects
    # Set the parsers for this viewset.
    parser_classes = (JSONParser, MultiPartParser, )
    # Set the serializer class for this viewset.
    serializer_class = LilyUserSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (OrderingFilter, DjangoFilterBackend)

    # OrderingFilter: set all possible fields to order by.
    ordering_fields = (
        'id', 'first_name', 'last_name', 'email', 'phone_number', 'is_active',
    )
    # OrderingFilter: set the default ordering fields.
    ordering = ('first_name', 'last_name', )
    # DjangoFilter: set the filter class.
    filter_class = LilyUserFilter

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        # TODO: find out what to do with linked objects when deactivating a user
        # TODO: remove the token page and include it in the normal account page
        queryset = super(LilyUserViewSet, self).get_queryset().filter(
            tenant_id=self.request.user.tenant_id
        ).exclude(
            first_name=''
        )

        # By default we filter out non-active users.
        is_active = self.request.query_params.get('is_active', 'True')

        # Value must be one of these, or it is ignored and we filter out non-active users.
        if is_active not in ['All', 'True', 'False']:
            is_active = 'True'

        # If the value is `All`, do not filter, otherwise filter the queryset on is_active status.
        if is_active in ['True', 'False']:
            queryset = queryset.filter(is_active=(is_active == 'True'))

        return queryset

    def get_object(self):
        """
        Get a user by pk

        If the pk is set to 'me', the currently logged in user will be returned

        Returns:
            serialized user instance
        """
        if self.kwargs['pk'] == 'me':
            return self.request.user
        else:
            return super(LilyUserViewSet, self).get_object()

    @list_route(methods=['GET', 'DELETE', 'POST'])
    def token(self, request, *args, **kwargs):
        """
        This view only returns the token of the currently logged in user

        GET returns the current token
        POST generates a new token
        DELETE removes the current token
        """
        if not has_required_tier(2):
            return Response(status=status.HTTP_403_FORBIDDEN)

        if request.method in ('DELETE', 'POST'):
            Token.objects.filter(user=request.user).delete()
            if request.method == 'DELETE':
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                Token.objects.create(user=request.user)

        serializer = LilyUserTokenSerializer(request.user)

        return Response(serializer.data)

    @list_route(methods=['PATCH'])
    def skip(self, request, pk=None):
        """
        Skip the first time email account setup.
        """
        user = self.request.user
        user.info.email_account_status = UserInfo.SKIPPED
        user.info.save()

        serializer = self.get_serializer(user, partial=True)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        picture = self.request.data.get('picture')

        if picture:
            if not self.request.FILES:
                if instance.picture:
                    # Picture property was set, but no files were sent.
                    # This means it's still the old picture.
                    self.request.data['picture'] = instance.picture
                else:
                    # Otherwise remove picture from request data to prevent errors.
                    del self.request.data['picture']

        return super(LilyUserViewSet, self).partial_update(request, args, kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Deactivate a user, but only if it's not the currently logged in user.
        """
        user_to_delete = self.get_object()

        if request.user.tenant.id != user_to_delete.tenant.id:
            return Response(status=status.HTTP_404_NOT_FOUND)

        tenant = user_to_delete.tenant

        # Prevent the user from deactivating him/herself.
        if request.user == user_to_delete:
            raise PermissionDenied

        user_to_delete.session_set.all().delete()

        # Don't call super, since that only fires another query using self.get_object().
        self.perform_destroy(user_to_delete)

        if settings.BILLING_ENABLED:
            tenant.billing.update_subscription(-1)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TwoFactorDevicesViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or disabling two factor devices.
    """
    def list(self, request):
        try:
            token_set = request.user.staticdevice_set.first().token_set.all()
        except AttributeError:
            token_set = []

        return Response({
            'default': get_info_text_for_device(default_device(request.user)),
            'backup_phone_numbers': [
                {
                    'id': phone.pk,
                    'number': mask_phone_number(format_phone_number(phone.number)),
                } for phone in backup_phones(request.user)
            ],
            'backup_tokens': [token.token for token in token_set],
        })

    @list_route(methods=['get', 'post', ])
    def regenerate_tokens(self, request):
        number_of_tokens = 10
        token_list = []

        device = request.user.staticdevice_set.get_or_create(name='backup')[0]
        device.token_set.all().delete()

        for n in range(number_of_tokens):
            token = device.token_set.create(token=StaticToken.random_token())
            token_list.append(token.token)

        return Response(token_list, status=status.HTTP_201_CREATED)

    @list_route(methods=['delete', ])
    def disable(self, request, pk=None):
        for device in devices_for_user(request.user):
            device.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['delete', ])
    def remove_phone(self, request, pk=None):
        try:
            request.user.phonedevice_set.get(name='backup', pk=pk).delete()
        except PhoneDevice.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)


class SessionViewSet(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """
    A simple ViewSet for listing or deleting sessions.
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Session.objects
    # Set the serializer class for this viewset.
    serializer_class = SessionSerializer

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return self.request.user.session_set.filter(expire_date__gt=timezone.now()).order_by('-last_activity')
