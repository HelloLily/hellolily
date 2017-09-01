from rest_framework import status

from lily.accounts.factories import AccountFactory, AccountStatusFactory
from lily.accounts.models import Account
from lily.contacts.api.serializers import ContactSerializer
from lily.contacts.factories import ContactFactory, FunctionFactory
from lily.contacts.models import Contact
from lily.socialmedia.factories import SocialMediaFactory
from lily.tags.factories import TagFactory
from lily.tests.utils import ElasticSearchFilterAPITest, GenericAPITestCase
from lily.utils.models.factories import AddressFactory, EmailAddressFactory, PhoneNumberFactory


class ContactTests(ElasticSearchFilterAPITest, GenericAPITestCase):
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
    search_attribute = 'full_name'

    def _create_object(self, with_relations=False, size=1, **kwargs):
        """
        Create an object with relations in the database using factories.
        """
        # Set a default tenant of the user.
        kwargs['tenant'] = self.user_obj.tenant if not kwargs.get('tenant') else kwargs['tenant']

        object_list = self.factory_cls.create_batch(size=size, **kwargs)

        for iteration in range(0, size):
            obj = object_list[iteration]

            if with_relations:
                obj.phone_numbers.add(*PhoneNumberFactory.create_batch(size=2, tenant=obj.tenant))
                obj.social_media.add(SocialMediaFactory(tenant=obj.tenant))
                obj.addresses.add(AddressFactory(tenant=obj.tenant))
                obj.email_addresses.add(EmailAddressFactory(tenant=obj.tenant))
                obj.functions.add(*FunctionFactory.create_batch(size=2, tenant=obj.tenant, contact=obj))
                obj.tags.add(*TagFactory.create_batch(size=2, tenant=obj.tenant, subject=obj))

        if size > 1:
            return object_list
        else:
            # If required size is 1, just give the object instead of a list.
            return object_list[0]

    def _create_object_stub(self, with_relations=False, size=1, **kwargs):
        """
        Create an object dict with relation dicts using factories.
        """
        object_list = []

        for iteration in range(0, size):
            obj = self.factory_cls.stub(**kwargs).__dict__
            del obj['tenant']

            if with_relations:
                # If relations are needed, override them, because a dict is needed instead of an instance.
                obj['phone_numbers'] = [PhoneNumberFactory.stub().__dict__, ]
                obj['social_media'] = [SocialMediaFactory.stub().__dict__, ]
                obj['addresses'] = [AddressFactory.stub().__dict__, ]
                obj['email_addresses'] = [EmailAddressFactory.stub().__dict__, ]
                obj['accounts'] = [AccountFactory.stub().__dict__, ]
                obj['accounts'][0]['status'] = {'id': AccountStatusFactory.create(tenant=self.user_obj.tenant).id}
                obj['tags'] = [TagFactory.stub().__dict__, ]

                del obj['accounts'][0]['tenant']

            object_list.append(obj)

        if size > 1:
            return object_list
        else:
            # If required size is 1, just give the object instead of a list.
            return object_list[0]

    def test_create_object_with_relations(self):
        """
        Test that the creation of a contact is successfull with relations.
        """
        contact = self._create_object_stub(with_relations=True)

        # Perform normal create.
        request = self.user.post(self.get_url(self.list_url), contact)
        self.assertStatus(request, status.HTTP_201_CREATED, contact)

        created_id = request.data['id']
        self.assertIsNotNone(created_id)
        db_obj = self.model_cls.objects.get(pk=created_id)
        self._compare_objects(db_obj, request.data)

        for field_name in ['phone_numbers', 'social_media', 'addresses', 'email_addresses', 'accounts', 'tags']:
            serializer = self.serializer_cls().fields[field_name].child
            self._compare_objects(getattr(db_obj, field_name).first(), request.data[field_name][0], serializer)

        account_id = request.data['accounts'][0]['id']  # For use in testcase #3

        # Check if id's are validated (create_only) and normal fields are validated.
        contact['phone_numbers'][0].update({'id': request.data['phone_numbers'][0]['id']})
        contact['accounts'].append({'id': 999})
        request = self.user.post(self.get_url(self.list_url), contact)
        self.assertStatus(request, status.HTTP_400_BAD_REQUEST, contact)
        self.assertEqual(request.data, {
            'phone_numbers': [{
                'id': ['Referencing to objects with an id is not allowed.']
            }],
            'accounts': [{
                'name': ['Company name already in use.']
            }, {
                'id': ['The id must point to an existing object.']}
            ]})

        # Check that deleted objects can't be referenced.
        Account.objects.get(pk=account_id).delete()
        contact['accounts'] = [{'id': account_id}, ]
        del contact['phone_numbers']  # Clear phone_numbers, only check account referencing.
        request = self.user.post(self.get_url(self.list_url), contact)
        self.assertStatus(request, status.HTTP_400_BAD_REQUEST, contact)
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

        request = self.user.post(self.get_url(self.list_url), stub_dict)
        self.assertStatus(request, status.HTTP_400_BAD_REQUEST, stub_dict)

        self.assertEqual(request.data, {
            'first_name': [
                'Please enter a valid first name.'
            ],
            'last_name': [
                'Please enter a valid last name.'
            ]
        })

    def test_update_object_with_relations(self):
        """
        Test that the update of a contact is successfull with relations.
        """
        contact = self._create_object(with_relations=True)
        new_contact = self._create_object_stub(with_relations=True)

        request = self.user.put(self.get_url(self.detail_url, kwargs={'pk': contact.pk}), new_contact)
        self.assertStatus(request, status.HTTP_200_OK, new_contact)

        created_id = request.data['id']
        self.assertIsNotNone(created_id)
        db_obj = self.model_cls.objects.get(pk=created_id)
        self._compare_objects(db_obj, request.data)

        for field_name in ['phone_numbers', 'social_media', 'addresses', 'email_addresses', 'accounts', 'tags']:
            serializer = self.serializer_cls().fields[field_name].child
            self._compare_objects(getattr(db_obj, field_name).first(), request.data[field_name][0], serializer)

    def test_create_object_with_account_relation(self):
        """
        Test that with the creation of a contact, the website field of a related account is untouched.
        """
        # Create a new contact. It also creates a related account with connected websites, used in this test case.
        contact = self._create_object(with_relations=True)
        account = contact.accounts.prefetch_related('websites').first()
        websites_before = list(account.websites.all())

        # Create a new contact and connect it to an existing account.
        contact = self._create_object_stub(with_relations=True)
        contact['accounts'] = [{'id': account.pk}, ]

        # Perform normal create.
        request = self.user.post(self.get_url(self.list_url), contact)
        self.assertStatus(request, status.HTTP_201_CREATED, contact)

        # Verify that the websites of the related account are the same as before the contact creation.
        websites_after = list(Account.objects.get(id=account.pk).websites.all())
        self.assertListEqual(websites_before, websites_after)

    def test_update_object_validation(self):
        # Update of the object
        pass

    def test_partial_update_object_with_relations(self):
        # Partial updates should still validate the related objects
        # Partial updates should amend to the relations
        pass

    def test_patch_with_deletion(self):
        contact = self._create_object(with_relations=True)

        data = {}
        fields = {
            'tags': list(contact.tags.all()),
            'accounts': list(contact.accounts.all()),
            'phone_numbers': list(contact.phone_numbers.all()),
        }

        for field_name, object_list in fields.items():
            data[field_name] = [{
                'id': object_list[0].pk,
                'is_deleted': True,
            }, {
                'id': object_list[1].pk,
            }]

        request = self.user.patch(self.get_url(self.detail_url, kwargs={'pk': contact.pk}), data)

        for field_name, object_list in fields.items():
            self.assertNotIn(
                object_list[0].pk,
                [item['id'] for item in request.data.get(field_name)],
                '%s %s was -not- deleted while it should have been.' % (field_name, object_list[0].pk)
            )
            self.assertIn(
                object_list[1].pk,
                [item['id'] for item in request.data.get(field_name)],
                '%s %s -was- deleted while it should have been.' % (field_name, object_list[1].pk)
            )
