from django.db import transaction
from django.db.models import Q
from django.utils.datastructures import MultiValueDictKeyError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.filters import OrderingFilter
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from tablib import UnsupportedFormat, Dataset

from lily.accounts.models import Account, AccountStatus
from lily.api.filters import ElasticSearchFilter
from lily.api.mixins import ModelChangesMixin, DataExistsMixin

from lily.calls.api.serializers import CallRecordSerializer
from lily.calls.models import CallRecord
from lily.contacts.api.serializers import ContactSerializer
from lily.contacts.models import Contact, Function
from lily.socialmedia.models import SocialMedia
from lily.utils.api.permissions import IsAccountAdmin
from lily.utils.models.models import EmailAddress, PhoneNumber, Address


class ContactViewSet(ModelChangesMixin, DataExistsMixin, viewsets.ModelViewSet):
    """
    Contacts are people you want to store the information of.

    retrieve:
    Returns the given contact.

    list:
    Returns a list of all the existing active contacts.

    create:
    Creates a new contact.

    update:
    Overwrites the whole contact with the given data.

    > Note: If Moneybird integration is setup each update will also send the contact's data to Moneybird.

    partial_update:
    Updates just the fields in the request data of the given contact.

    > Note: If Moneybird integration is setup each update will also send the contact's data to Moneybird.

    delete:
    Deletes the given contact.

    changes:
    Returns all the changes performed on the given contact.
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Contact.objects
    # Set the serializer class for this viewset.
    serializer_class = ContactSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (ElasticSearchFilter, OrderingFilter,)

    # ElasticSearchFilter: set the model type.
    model_type = 'contacts_contact'
    # OrderingFilter: set all possible fields to order by.
    ordering_fields = (
        'id', 'first_name', 'last_name', 'full_name', 'gender', 'gender_display', 'salutation', 'salutation_display',
    )
    # OrderingFilter: set the default ordering fields.
    ordering = ('last_name', 'first_name',)

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        if 'filter_deleted' in self.request.GET:
            if self.request.GET.get('filter_deleted') == 'False':
                return super(ContactViewSet, self).get_queryset()

        return super(ContactViewSet, self).get_queryset().filter(is_deleted=False)

    @swagger_auto_schema(auto_schema=None)
    @detail_route(methods=['GET', ])
    def calls(self, request, pk=None):
        contact = self.get_object()

        phone_numbers = contact.phone_numbers.all().values_list('number', flat=True)

        calls = CallRecord.objects.filter(
            Q(caller__number__in=phone_numbers) | Q(destination__number__in=phone_numbers)
        ).order_by(
            '-start'
        )[:100]

        serializer = CallRecordSerializer(calls, many=True, context={'request': request})

        return Response(serializer.data)


class ContactImport(APIView):
    permission_classes = (IsAuthenticated, IsAccountAdmin, )
    classes = (FileUploadParser, )
    swagger_schema = None

    def post(self, request):
        try:
            csv_file = request.data['csv']
            imported_data = Dataset().load(csv_file.read())
        except MultiValueDictKeyError:
            return Response({'file_contacts': {'Please choose a CSV file to import'}}, status=status.HTTP_409_CONFLICT)
        except UnsupportedFormat:
            return Response({'file_contacts': {'CSV file not properly formatted'}}, status=status.HTTP_409_CONFLICT)

        # The following set of fields should be present as headers in the uploaded file.
        required_fields = {u'first name', u'last name'}
        # The following set of fields are optional.
        optional_fields = {u'company name', u'email address', u'phone number', u'address', u'postal code', u'city',
                           u'twitter', u'linkedin', u'mobile'}

        # The following headers are present in the uploaded file.
        available_in_upload = set(imported_data.headers)

        # Use set operations to determine which of the headers in the uploaded file are missing, optional or extra.
        missing_in_upload = required_fields - (required_fields & available_in_upload)
        optional_in_upload = optional_fields & available_in_upload
        extra_in_upload = available_in_upload - (required_fields | optional_fields)

        if bool(missing_in_upload):
            return Response(
                {'file_contacts': {'The follwing columns are missing: {0}'.format(', '.join(missing_in_upload))}},
                status=status.HTTP_409_CONFLICT)

        tenant = self.request.user.tenant
        duplicate = []
        error = []
        created = []
        for row in imported_data.dict:
            first_name = row.get(u'first name')
            last_name = row.get(u'last name')
            full_name = u'{0} {1}'.format(first_name, last_name)

            # Check if the contact already exists, possibly when the user re-uploads the same file.
            if Contact.objects.filter(first_name=first_name, last_name=last_name, tenant=tenant,
                                      is_deleted=False).exists():
                # A small chance people have the same name, so acceptable to have wrongly marked duplicates.
                duplicate.append(full_name)
                continue

            account = None
            email_address = None
            phone_number = None
            address = None
            twitter = None
            linkedin = None
            mobile = None
            try:
                # Use atomic to rollback all intermediate database actions if an error occurs in just one of them.
                with transaction.atomic():
                    # All the extra fields excluding 'company' that are present in the upload are placed in the
                    # description field.
                    description = u''
                    extra_in_upload_wo_company = set(extra_in_upload)
                    extra_in_upload_wo_company.discard(u'company name')
                    for field in extra_in_upload_wo_company:
                        if row.get(field):
                            description += '{0}: {1}\n'.format(field.capitalize(), row.get(field))

                    contact = Contact(first_name=first_name,
                                      last_name=last_name,
                                      tenant=tenant,
                                      description=description)
                    # Skip the signal at this moment, so on a rollback the instance isn't still in the search index.
                    contact.skip_signal = True
                    contact.save()

                    if u'company name' in optional_in_upload and row.get(u'company name'):
                        company_name = row.get(u'company name')
                        # Not using get_or_create() to make use of the skip_signal construction.
                        try:
                            account = Account.objects.get(name=company_name, tenant=tenant, is_deleted=False)
                        except Account.DoesNotExist:
                            account_status = AccountStatus.objects.get(name='Relation', tenant=tenant)
                            account = Account(name=company_name,
                                              tenant=tenant,
                                              status=account_status)
                            account.skip_signal = True
                            account.save()

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

                    if u'twitter' in optional_in_upload and row.get(u'twitter'):
                        twitter = SocialMedia(name='twitter',
                                              username=row.get(u'twitter'),
                                              profile_url='https://twitter.com/{0}'.format(row.get(u'twitter')),
                                              tenant=tenant)
                        twitter.skip_signal = True
                        twitter.save()

                    if u'linkedin' in optional_in_upload and row.get(u'linkedin'):
                        linkedin = SocialMedia(name='linkedin',
                                               username=row.get(u'linkedin'),
                                               profile_url='https://www.linkedin.com/in/{0}'.format(
                                                   row.get(u'linkedin')),
                                               tenant=tenant)
                        linkedin.skip_signal = True
                        linkedin.save()

                    if u'mobile' in optional_in_upload and row.get(u'mobile'):
                        mobile = PhoneNumber(
                            number=row.get(u'mobile'),
                            tenant=tenant,
                            type='mobile',
                        )
                        mobile.skip_signal = True
                        mobile.save()

            except Exception:
                # On an exception all databaase actions are rolled back. Because of the skip_signal=True no data is
                # added to the search index.
                error.append(full_name)
            else:
                if email_address:
                    email_address.skip_signal = False
                    email_address.save()
                    contact.email_addresses.add(email_address)
                if phone_number:
                    phone_number.skip_signal = False
                    phone_number.save()
                    contact.phone_numbers.add(phone_number)
                if address:
                    address.skip_signal = False
                    address.save()
                    contact.addresses.add(address)

                    contact.skip_signal = False
                    contact.save()
                if twitter:
                    twitter.skip_signal = False
                    twitter.save()
                    contact.social_media.add(twitter)
                if linkedin:
                    linkedin.skip_signal = False
                    linkedin.save()
                    contact.social_media.add(linkedin)
                if account:
                    account.skip_signal = False
                    account.save()

                    Function.objects.create(account=account, contact=contact)
                if mobile:
                    mobile.skip_signal = False
                    mobile.save()
                    contact.phone_numbers.add(mobile)

                created.append(full_name)

        return Response({'created': created, 'duplicate': duplicate, 'error': error}, status=status.HTTP_201_CREATED)
