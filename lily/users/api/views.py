from datetime import date
from hashlib import sha256

from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse_lazy
from django.core.validators import validate_email
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_filters import FilterSet
from django_filters import rest_framework as filters
from django_filters.rest_framework import BooleanFilter
from django_otp import devices_for_user
from django_otp.plugins.otp_static.models import StaticToken
from rest_framework import mixins, viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from two_factor.models import PhoneDevice
from two_factor.templatetags.two_factor import mask_phone_number, format_phone_number
from two_factor.utils import default_device, backup_phones
from user_sessions.models import Session
from templated_email import send_templated_mail

from lily.api.filters import ElasticSearchFilter
from lily.api.mixins import ElasticModelMixin
from lily.utils.api.permissions import IsAccountAdmin
from lily.utils.functions import has_required_tier, post_intercom_event

from .utils import get_info_text_for_device
from .serializers import (
    TeamSerializer, LilyUserSerializer, LilyUserTokenSerializer, SessionSerializer, UserInviteSerializer,
    BasicLilyUserSerializer
)
from ..models import Team, LilyUser, UserInvite, UserSettings


class TeamFilter(FilterSet):
    class Meta:
        model = Team
        fields = ['name', ]


class TeamViewSet(viewsets.ModelViewSet):
    """
    List all teams assigned to the current user.
    """
    model = Team
    serializer_class = TeamSerializer
    filter_class = TeamFilter
    queryset = Team.objects
    permission_classes = (IsAuthenticated, IsAccountAdmin,)
    unrestricted_methods = ['GET']
    swagger_schema = None

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
    swagger_schema = None

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
        has_errors = False

        for invite in invites:
            first_name = invite.get('first_name')
            email = invite.get('email')
            valid_email = True
            error = {}

            try:
                validate_email(email)
            except:
                valid_email = False

            if not first_name or not email or not valid_email:
                error = {
                    'name': [_('Please enter a first name and valid email address')],
                }
                has_errors = True

            if LilyUser.objects.filter(email=email, is_active=True).exists():
                error = {
                    'name': [_('A user with this email address already exists')],
                }
                has_errors = True

            errors.append(error)

            if UserInvite.objects.filter(email=email).exists():
                # Send a new invite if one was already sent.
                UserInvite.objects.filter(email=email).delete()

        if has_errors:
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
                template_name='users/email/invitation.email',
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
    is_active = BooleanFilter()

    class Meta:
        model = LilyUser
        fields = {
            'is_active': ['exact', ],
            'teams': ['isnull', ],
        }


class LilyUserViewSet(ElasticModelMixin, viewsets.ModelViewSet):
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
    queryset = LilyUser.elastic_objects
    # Set the parsers for this viewset.
    parser_classes = (JSONParser, MultiPartParser,)
    # Set the serializer class for this viewset.
    serializer_class = LilyUserSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (ElasticSearchFilter, OrderingFilter, filters.DjangoFilterBackend)
    swagger_schema = None

    # OrderingFilter: set all possible fields to order by.
    ordering_fields = ('first_name', 'last_name', 'email', 'phone_number', 'is_active')
    # OrderingFilter: set the default ordering fields.
    ordering = ('first_name', 'last_name',)
    # SearchFilter: set the fields that can be searched on.
    search_fields = ('full_name', 'email', 'phone_number', 'position', 'internal_number')
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
        is_active_param = self.request.query_params.get('is_active', 'True')

        if is_active_param in (True, 'True', 'true', '1'):
            is_active = True
        elif is_active_param in (False, 'False', 'false', '0'):
            is_active = False
        elif is_active_param in ('All', 'all'):
            is_active = None
        else:
            is_active = True

        # If the value is `All`, do not filter, otherwise filter the queryset on is_active status.
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        data = request.data.copy()  # Make a copy because the QueryDict instance is immutable.
        picture = data.get('picture')

        if picture and not request.FILES:
            # Picture property was set, but no files were sent.
            # This means we clear it.
            data['picture'] = None

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

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

    @list_route(methods=['GET', ])
    def unassigned(self, request):
        # Retrieve users that aren't assigned to a team.
        queryset = self.get_queryset().filter(teams__isnull=True)
        filtered_queryset = self.filter_class(request.GET, queryset=queryset).qs
        #  Use the basic serializer to excluded nested fields.
        serializer = BasicLilyUserSerializer(filtered_queryset, context={'request': request}, many=True)
        return Response({'results': serializer.data})

    @detail_route(methods=['GET', 'PATCH'], url_path='settings')
    def user_settings(self, request, pk=None):
        user = self.get_object()

        if not user.settings:
            user.settings = UserSettings.objects.create()
            user.save()

        method = request.method
        data = request.data

        if method == 'GET':
            component = request.query_params.get('component')

            user_settings = user.settings.data

            if component:
                user_settings = user_settings.get(component)

            return Response({'results': user_settings})
        elif method == 'PATCH':
            # Key will be component's name, so no need to store it again.
            component = data.pop('component')

            if not component:
                # Since there is no way of knowing what to store the data as,
                # the request is considered invalid.
                return Response(status=status.HTTP_400_BAD_REQUEST)

            # Make sure the key is always set.
            user.settings.data.setdefault(component, {})
            # Update the values for the component with the actual data.
            user.settings.data[component].update(data)
            user.settings.save()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class TwoFactorDevicesViewSet(viewsets.ViewSet):
    swagger_schema = None

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

        return Response({'results': token_list}, status=status.HTTP_201_CREATED)

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
    swagger_schema = None

    """
    A simple ViewSet for listing or deleting sessions.
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Session.objects
    # Set the serializer class for this viewset.
    serializer_class = SessionSerializer
    swagger_schema = None

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return self.request.user.session_set.filter(expire_date__gt=timezone.now()).order_by('-last_activity')
