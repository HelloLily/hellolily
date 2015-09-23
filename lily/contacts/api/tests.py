from rest_framework import status
from rest_framework.reverse import reverse

from lily.accounts.factories import AccountFactory
from lily.accounts.models import Account
from lily.contacts.api.serializers import ContactSerializer
from lily.contacts.factories import ContactFactory, FunctionFactory
from lily.contacts.models import Contact
from lily.socialmedia.factories import SocialMediaFactory
from lily.tags.factories import TagFactory
from lily.tests.utils import GenericAPITestCase
from lily.utils.models.factories import PhoneNumberFactory, EmailAddressFactory, AddressFactory


class ContactTests(GenericAPITestCase):
    """
    Class containing tests for the contact API.

    Note that each test removes the 'id' key from the response dict.
    That's because it's a hassle to compare IDs since they change when the test order is changed.
    """
    list_url = 'contact-list'
    detail_url = 'contact-detail'
    factory_cls = ContactFactory
    model_cls = Contact
    serializer_cls = ContactSerializer

    def _create_object_with_relations(self):
        """
        Create an object with relations in the database using factories.
        """
        contact = self.factory_cls(tenant=self.user_obj.tenant)
        contact.phone_numbers.add(PhoneNumberFactory(tenant=contact.tenant))
        contact.social_media.add(SocialMediaFactory(tenant=contact.tenant))
        contact.addresses.add(AddressFactory(tenant=contact.tenant))
        contact.email_addresses.add(EmailAddressFactory(tenant=contact.tenant))
        contact.functions.add(FunctionFactory(tenant=contact.tenant, contact=contact))
        contact.tags.add(TagFactory(tenant=contact.tenant, subject=contact))

        return contact

    def _create_object_stub_with_relations(self):
        """
        Create an object dict with relation dicts using factories.
        """
        contact = self.factory_cls.stub().__dict__
        contact['phone_numbers'] = [PhoneNumberFactory.stub().__dict__, ]
        contact['social_media'] = [SocialMediaFactory.stub().__dict__, ]
        contact['addresses'] = [AddressFactory.stub().__dict__, ]
        contact['email_addresses'] = [EmailAddressFactory.stub().__dict__, ]
        contact['accounts'] = [AccountFactory.stub().__dict__, ]
        contact['tags'] = [TagFactory.stub().__dict__, ]

        del contact['tenant']
        del contact['accounts'][0]['tenant']

        return contact

    def test_create_object_with_relations(self):
        """
        Test that the creation of an account is succesfull with relations.
        """
        contact = self._create_object_stub_with_relations()

        # Perform normal create
        request = self.user.post(reverse(self.list_url), contact)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        created_id = request.data['id']
        self.assertIsNotNone(created_id)
        db_obj = self.model_cls.objects.get(pk=created_id)
        self._compare_objects(db_obj, request.data)

        for field_name in ['phone_numbers', 'social_media', 'addresses', 'email_addresses', 'accounts', 'tags']:
            serializer = self.serializer_cls().fields[field_name].child
            self._compare_objects(getattr(db_obj, field_name).first(), request.data[field_name][0], serializer)

        account_id = request.data['accounts'][0]['id']  # For use in testcase #3

        # Check if id's are validated (create_only) and normal fields are validated
        contact['phone_numbers'][0].update({'id': request.data['phone_numbers'][0]['id']})
        contact['accounts'].append({'id': 999})
        request = self.user.post(reverse(self.list_url), contact)
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(request.data, {
            'phone_numbers': [{
                'id': ['Referencing to objects with an id is not allowed.']
            }],
            'accounts': [{
                'name': ['Company name already in use.']
            }, {
                'id': ['The id must point to an existing object.']}
            ]})

        # Check that deleted objects can't be referenced
        Account.objects.get(pk=account_id).delete()
        contact['accounts'] = [{'id': account_id}, ]
        del contact['phone_numbers']  # Clear phone_numbers, obly check account referencing
        request = self.user.post(reverse(self.list_url), contact)
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(request.data, {
            'accounts': [{
                'id': ['The id must point to an existing object.']
            }]
        })

    def test_create_object_validation(self):
        """
        Test that the create of a contact is validated properly.
        """
        stub_dict = self.model_cls().__dict__
        del stub_dict['_state']

        request = self.user.post(reverse(self.list_url), stub_dict)
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(request.data, {
            'last_name': [
                'Please enter a valid name.'
            ]
        })

    def test_update_object_with_relations(self):
        """
        Test that the update of an account is succesfull with relations.
        """
        contact = self._create_object_with_relations()
        new_contact = self._create_object_stub_with_relations()

        request = self.user.put(reverse(self.detail_url, kwargs={'pk': contact.pk}), new_contact)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        created_id = request.data['id']
        self.assertIsNotNone(created_id)
        db_obj = self.model_cls.objects.get(pk=created_id)
        self._compare_objects(db_obj, request.data)

        for field_name in ['phone_numbers', 'social_media', 'addresses', 'email_addresses', 'accounts', 'tags']:
            serializer = self.serializer_cls().fields[field_name].child
            self._compare_objects(getattr(db_obj, field_name).first(), request.data[field_name][0], serializer)

    def test_update_object_validation(self):
        # Update of the object
        pass

    def test_partial_update_object_with_relations(self):
        # Partial updates should still validate the related objects
        # Partial updates should amend to the relations
        pass




