from django.db import transaction
from django.db.models import Q
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.filters import OrderingFilter, DjangoFilterBackend
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from tablib import UnsupportedFormat, Dataset

from lily.accounts.models import Account, AccountStatus
from lily.api.filters import ElasticSearchFilter
from lily.api.mixins import ModelChangesMixin, ElasticModelMixin

from lily.calls.api.serializers import CallRecordSerializer
from lily.calls.models import CallRecord
from lily.contacts.api.serializers import ContactSerializer
from lily.contacts.models import Contact, Function
from lily.socialmedia.models import SocialMedia
from lily.utils.api.permissions import IsAccountAdmin
from lily.utils.functions import uniquify
from lily.utils.models.models import EmailAddress, PhoneNumber, Address


class ContactViewSet(ElasticModelMixin, ModelChangesMixin, viewsets.ModelViewSet):
    """
    Returns a list of all **active** contacts in the system.

    #Search#
    Searching is enabled on this API.

    To search, provide a field name to search on followed by the value you want to search for to the search parameter.

    #Ordering#
    Ordering is enabled on this API.

    To order, provide a comma seperated list to the ordering argument. Use `-` minus to inverse the ordering.

    #Examples#
    - plain: `/api/contacts/`
    - search: `/api/contacts/?search=subject:Doremi`
    - order: `/api/contacts/?ordering=subject,-id`

    #Returns#
    * List of cases with related fields
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Contact.elastic_objects
    # Set the serializer class for this viewset.
    serializer_class = ContactSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (ElasticSearchFilter, OrderingFilter, DjangoFilterBackend, )

    # OrderingFilter: set all possible fields to order by.
    ordering_fields = ('first_name', 'last_name', 'created', 'modified', 'accounts__name', 'status', )
    # OrderingFilter: set the default ordering fields.
    ordering = ('last_name', 'first_name', )
    # SearchFilter: set the fields that can be searched on.
    search_fields = ('accounts__name', 'accounts__phone_numbers', 'description', 'email_addresses',
                     'full_name', 'phone_numbers', 'tags', )
    filter_fields = ('accounts', )

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        if 'filter_deleted' in self.request.GET:
            if self.request.GET.get('filter_deleted') == 'False':
                return super(ContactViewSet, self).get_queryset()

        return super(ContactViewSet, self).get_queryset().filter(is_deleted=False)

    @list_route(methods=['patch', ])
    def toggle_activation(self, request):
        """
        Toggle if the contact is active at account.
        """
        contact_id = request.data.get('contact')
        account_id = request.data.get('account')
        is_active = request.data.get('is_active')

        try:
            func = Function.objects.get(contact=contact_id, account=account_id)
        except Function.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            func.is_active = is_active
            func.save()

            return Response(status=status.HTTP_200_OK)

    @detail_route(methods=['GET', ])
    def calls(self, request, pk=None):
        contact = self.get_object()

        phone_numbers = contact.phone_numbers.all().values_list('number', flat=True)
        phone_numbers = uniquify(phone_numbers)  # Filter out double numbers.

        calls = CallRecord.objects.filter(
            Q(caller__number__in=phone_numbers) | Q(destination__number__in=phone_numbers)
        )

        page = self.paginate_queryset(calls)

        return self.get_paginated_response(
            CallRecordSerializer(page, many=True, context={'request': request}).data
        )


class ContactImport(APIView):
    permission_classes = (IsAuthenticated, IsAccountAdmin, )
    classes = (FileUploadParser, )

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
                           u'twitter', u'linkedin'}

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
            full_name = "{0} {1}".format(first_name, last_name)

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
            try:
                # Use atomic to rollback all intermediate database actions if an error occurs in just one of them.
                with transaction.atomic():
                    # All the extra fields excluding 'company' that are present in the upload are placed in the
                    # description field.
                    description = ''
                    extra_in_upload_wo_company = set(extra_in_upload)
                    extra_in_upload_wo_company.discard(u'company name')
                    for field in extra_in_upload_wo_company:
                        description += '{0}: {1}\n'.format(field, row.get(field))

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
                            account = Account.objects.get(name=company_name, tenant=tenant)
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

                created.append(full_name)

        return Response({'created': created, 'duplicate': duplicate, 'error': error}, status=status.HTTP_201_CREATED)
