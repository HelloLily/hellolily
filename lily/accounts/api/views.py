from django.db import transaction
from django.db.models import Q
from django.utils.datastructures import MultiValueDictKeyError
from django_filters import FilterSet
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
from lily.calls.api.serializers import CallRecordSerializer
from lily.calls.models import CallRecord
from lily.utils.functions import uniquify

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
    filter_backends = (ElasticSearchFilter, OrderingFilter, )

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

    @detail_route(methods=['GET', ])
    def calls(self, request, pk=None):
        account = self.get_object()

        phone_numbers = account.phone_numbers.all().values_list('number', flat=True)

        contact_list = account.get_contacts()

        for contact in contact_list:
            phone_numbers += contact.phone_numbers.all().values_list('number', flat=True)

        phone_numbers = uniquify(phone_numbers)  # Filter out double numbers.

        calls = CallRecord.objects.filter(
            Q(caller__number__in=phone_numbers) | Q(destination__number__in=phone_numbers)
        )

        page = self.paginate_queryset(calls)

        return self.get_paginated_response(
            CallRecordSerializer(page, many=True, context={'request': request}).data
        )


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
