from django.db import transaction
from django.utils.datastructures import MultiValueDictKeyError
from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import detail_route
from rest_framework import status
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from tablib import Dataset, UnsupportedFormat

from lily.api.filters import ElasticSearchFilter
from lily.api.mixins import ModelChangesMixin
from lily.calls.api.serializers import CallSerializer
from lily.calls.models import Call
from lily.users.models import LilyUser

from lily.socialmedia.models import SocialMedia
from lily.utils.models.models import EmailAddress, PhoneNumber, Address
from .serializers import AccountSerializer, AccountStatusSerializer
from ..models import Account, AccountStatus, Website


class AccountFilter(FilterSet):
    class Meta:
        model = Account
        fields = {
            'addresses': ['exact', ],
            'assigned_to': ['exact', ],
            'bankaccountnumber': ['exact', ],
            'bic': ['exact', ],
            'cocnumber': ['exact', ],
            'contacts': ['exact', ],
            'created': ['exact', 'lt', 'lte', 'gt', 'gte', ],
            'customer_id': ['exact', ],
            'description': ['exact', ],
            'email_addresses': ['exact', ],
            'flatname': ['exact', ],
            'iban': ['exact', ],
            'legalentity': ['exact', ],
            'id': ['exact', ],
            'modified': ['exact', ],
            'name': ['exact', ],
            'phone_numbers': ['exact', ],
            'social_media': ['exact', ],
            'status': ['exact', ],
            'taxnumber': ['exact', ],
            'websites': ['exact', ],
        }


class AccountViewSet(ModelChangesMixin, ModelViewSet):
    """
    Returns a list of all **active** accounts in the system.

    #Search#
    Searching is enabled on this API.

    To search, provide a field name to search on followed by the value you want
    to search for to the search parameter.

    #Returns#
    * List of accounts with related fields
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Account.objects
    # Set the serializer class for this viewset.
    serializer_class = AccountSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (ElasticSearchFilter, OrderingFilter, DjangoFilterBackend, )

    # ElasticSearchFilter: set the model type.
    model_type = 'accounts_account'
    # OrderingFilter: set all possible fields to order by.
    ordering_fields = ('id', )
    # OrderingFilter: set the default ordering fields.
    ordering = ('id', )
    # DjangoFilter: set the filter class.
    filter_class = AccountFilter

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        if 'filter_deleted' in self.request.GET:
            if self.request.GET.get('filter_deleted') == 'False':
                return super(AccountViewSet, self).get_queryset()

        return super(AccountViewSet, self).get_queryset().filter(is_deleted=False)

    @detail_route(methods=['GET'])
    def calls(self, request, pk=None):
        """
        Gets the calls for the given contact.
        """
        account_phone_numbers = []
        calls = []
        account = self.get_object()
        contacts = account.get_contacts()
        tenant = self.request.user.tenant

        # Get calls made from a phone number which belongs to the account.
        for number in account.phone_numbers.all():
            account_phone_numbers.append(number.number)

        call_objects = Call.objects.filter(
            status=Call.ANSWERED,
            type=Call.INBOUND,
            caller_number__in=account_phone_numbers,
            created__isnull=False,
        )

        if call_objects:
            calls = CallSerializer(call_objects, many=True).data

            for call in calls:
                call['account'] = account.name

                if len(contacts) == 1:
                    call['contact'] = contacts[0].full_name

                user = LilyUser.objects.filter(internal_number=call.get('internal_number'), tenant=tenant).first()

                if user:
                    call['user'] = user.full_name

        # Get calls for every phone number of every contact in an account.
        for contact in contacts:
            contact_phone_numbers = []

            for number in contact.phone_numbers.all():
                contact_phone_numbers.append(number.number)

            call_objects = Call.objects.filter(
                status=Call.ANSWERED,
                type=Call.INBOUND,
                caller_number__in=contact_phone_numbers,
                created__isnull=False,
            )

            if call_objects:
                contact_calls = CallSerializer(call_objects, many=True).data

                for call in contact_calls:
                    add_call = True

                    for account_call in calls:
                        if call.get('id') == account_call.get('id'):
                            add_call = False
                            account_call['contact'] = contact.full_name

                    if add_call:
                        call['contact'] = contact.full_name

                        user = LilyUser.objects.filter(
                            internal_number=call.get('internal_number'),
                            tenant=tenant,
                        ).first()

                        if user:
                            call['user'] = user.full_name

                        calls.append(call)

        return Response({'objects': calls})


class AccountStatusViewSet(ModelViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = AccountStatus.objects
    # Set the serializer class for this viewset.
    serializer_class = AccountStatusSerializer

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(AccountStatusViewSet, self).get_queryset().all()


class AccountImport(APIView):

    classes = (FileUploadParser, )

    def post(self, request):
        try:
            csv_file = request.data['csv']
            imported_data = Dataset().load(csv_file.read())
        except MultiValueDictKeyError:
            return Response({'file': {'No CSV file choosen'}}, status=status.HTTP_409_CONFLICT)
        except UnsupportedFormat:
            return Response({'file': {'CSV file not properly formated'}}, status=status.HTTP_409_CONFLICT)

        # The following set of fields should be present as headers in the uploaded file.
        required_fields = {u'name'}
        # The following set of fields are optional.
        optional_fields = {u'website', u'email address', u'phone number', u'twitter', u'address', u'postal code',
                           u'city'}

        # The following headers are present in the uploaded file.
        available_in_upload = set(imported_data.headers)

        # Use set operations to determine which of the headers in the uploaded file are missing, optional or extra.
        missing_in_upload = required_fields - (required_fields & available_in_upload)
        optional_in_upload = optional_fields & available_in_upload
        extra_in_upload = available_in_upload - (required_fields | optional_fields)

        if bool(missing_in_upload):
            return Response({'file': {'The follwing columns are missing: {0}'.format(', '.join(missing_in_upload))}},
                            status=status.HTTP_409_CONFLICT)

        tenant = self.request.user.tenant
        duplicate = []
        error = []
        created = []
        for row in imported_data.dict:
            name = row.get(u'name')

            # Check if the account already exists, possibly when the user re-uploads the same file.
            if Account.objects.filter(name=name, tenant=tenant, is_deleted=False).exists():
                duplicate.append(name)
                continue

            website = None
            email_address = None
            phone_number = None
            twitter = None
            address = None
            try:
                # Use atomic to rollback all intermediate database actions if an error occurs in just one of them.
                with transaction.atomic():
                    description = ''
                    # All the extra fields that are present in the upload are used in the description field.
                    for field in extra_in_upload:
                        description += '{0}: {1}\n'.format(field, row.get(field))

                    account_status = AccountStatus.objects.get(name='Relation', tenant=tenant)
                    account = Account(name=name,
                                      tenant=tenant,
                                      status=account_status,
                                      description=description)
                    # Skip the signal at this moment, so on a rollback the instance isn't still in the search index.
                    account.skip_signal = True
                    account.save()

                    if u'website' in optional_in_upload and row.get(u'website'):
                        website = Website(website=row.get(u'website'),
                                          is_primary=True, account=account,
                                          tenant=tenant)
                        website.skip_signal = True
                        website.save()

                    if u'email address' in optional_in_upload and row.get(u'email address'):
                        email_address = EmailAddress(email_address=row.get(u'email address'),
                                                     status=EmailAddress.PRIMARY_STATUS,
                                                     tenant=tenant)
                        email_address.skip_signal = True
                        email_address.save()

                    if u'phone number' in optional_in_upload and row.get(u'phone number'):
                        phone_number = PhoneNumber(number=row.get(u'phone number'),
                                                   tenant=tenant)
                        phone_number.skip_signal = True
                        phone_number.save()

                    if u'twitter' in optional_in_upload and row.get(u'twitter'):
                        twitter = SocialMedia(name='twitter',
                                              username=row.get(u'twitter'),
                                              profile_url='https://twitter.com/{0}'.format(row.get(u'twitter')),
                                              tenant=tenant)
                        twitter.skip_signal = True
                        twitter.save()

                    # An Address consists of multiple, optional fields. So create or update the instance.
                    if u'address' in optional_in_upload and row.get(u'address'):
                        address = Address(address=row.get(u'address'),
                                          type='visiting',
                                          tenant=tenant)
                        address.skip_signal = True
                        address.save()

                    if u'postal code' in optional_in_upload and row.get(u'postal code'):
                        if address:
                            address.postal_code = row.get(u'postal code')
                        else:
                            address = Address(postal_code=row.get(u'postal code'),
                                              type='visiting',
                                              tenant=tenant)
                        address.skip_signal = True
                        address.save()

                    if u'city' in optional_in_upload and row.get(u'city'):
                        if address:
                            address.city = row.get(u'city')
                        else:
                            address = Address(city=row.get(u'city'),
                                              type='visiting',
                                              tenant=tenant)
                        address.skip_signal = True
                        address.save()

            except Exception:
                # On an exception all databaase actions are rolled back. Because of the skip_signal=True no data is
                # added to the search index.
                error.append(name)
            else:
                if website:
                    website.skip_signal = False
                    website.save()
                    account.websites.add(website)
                if email_address:
                    email_address.skip_signal = False
                    email_address.save()
                    account.email_addresses.add(email_address)
                if phone_number:
                    phone_number.skip_signal = False
                    phone_number.save()
                    account.phone_numbers.add(phone_number)
                if twitter:
                    twitter.skip_signal = False
                    twitter.save()
                    account.social_media.add(twitter)
                if address:
                    address.skip_signal = False
                    address.save()
                    account.addresses.add(address)

                account.skip_signal = False
                account.save()

                created.append(name)

        return Response({'created': created, 'duplicate': duplicate, 'error': error},
                        status=status.HTTP_201_CREATED)
