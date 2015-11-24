from django.contrib.auth.hashers import make_password
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from lily.accounts.models import Account
from lily.tenant.middleware import set_current_user
from lily.tenant.models import Tenant
from lily.users.factories import LilyUserFactory
from lily.users.models import LilyUser


class AccountTests(APITestCase):
    """
    Class containing tests for the account API.

    Note that each test removes the 'id' key from the response dict.
    That's because it's a hassle to compare IDs since they change when the test order is changed.
    """

    # Dict containing standard compare data which can be edited accordingly in each test
    default_compare_data = {
        'addresses': [],
        'assigned_to': None,
        'bankaccountnumber': '',
        'bic': '',
        'cocnumber': '',
        'customer_id': '',
        'description': '',
        'email_addresses': [],
        'iban': '',
        'legalentity': '',
        'name': 'Test account',
        'phone_numbers': [],
        'social_media': [],
        'tags': [],
        'taxnumber': '',
        'websites': []
    }

    @classmethod
    def setUpClass(cls):
        """
        Creates a user and logs it in before running the account tests.
        """
        set_current_user(None)
        # Remove leftovers from previous tests
        LilyUser.objects.all().delete()
        Tenant.objects.all().delete()

        cls.user = LilyUserFactory.create(is_active=True, email='user1@lily.com', password=make_password('test'))

        cls.client = APIClient()
        cls.client.login(email='user1@lily.com', password='test')

    @classmethod
    def tearDownClass(cls):
        set_current_user(None)
        LilyUser.objects.all().delete()
        Tenant.objects.all().delete()

    def create_account(self, extra_data=None):
        data = {
            'name': 'Test account',
            'description': ''
        }

        if extra_data:
            data.update(extra_data)

        url = reverse('account-list')

        response = AccountTests.client.post(url, data, format='json')

        return Account.objects.get(pk=response.data['id'])

    def test_simple_create_account(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('account-list')

        post_data = {
            'name': 'Test account'
        }

        response = AccountTests.client.post(url, post_data, format='json')

        self.assertGreater(response.data.get('id', 0), 0)
        del response.data['id']

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, self.default_compare_data)

    def test_simple_create_account_duplicate_name(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('account-list')

        account = self.create_account()

        post_data = {
            'name': 'Test account'
        }

        compare_data = {
            'name': ['Company name already in use.']
        }

        response = AccountTests.client.post(url, post_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, compare_data)

    def test_simple_create_account_no_data(self):
        """
        Ensure posting nothing produces an error.
        """
        url = reverse('account-list')

        compare_data = {
            'name': ['This field is required.']
        }

        response = AccountTests.client.post(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, compare_data)

    def test_simple_create_account_assigned_to_error(self):
        """
        Ensure posting nothing produces an error.
        """
        url = reverse('account-list')

        post_data = {
            'name': 'Test account',
            'assigned_to': 123
        }

        compare_data = {
            'assigned_to': ['Invalid pk "123" - object does not exist.']
        }

        response = AccountTests.client.post(url, post_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, compare_data)

    def test_create_account_full_data(self):
        """
        Ensure we can create a new account object with multiple related fields.
        """
        url = reverse('account-list')

        post_data = {
            'name': 'Test account',
            'description': 'This is a test description',
            'customer_id': '1234',
            'assigned_to': AccountTests.user.id,
            'email_addresses': [{
                'email_address': 'test1@account.com'
            }],
            'phone_numbers': [{
                'raw_input': '0612345678',
                'type': 'mobile'
            }],
            'websites': [{
                'website': 'www.domain.com'
            }],
            'addresses': [{
                'street': 'Street',
                'street_number': '123',  # Post string on purpose to make sure it gets saved as an integer
                'complement': 'a',
                'postal_code': '1234AB',
                'city': 'Somewhere',
                'country': 'NL',
                'type': 'visiting',
            }]
        }

        compare_data = self.default_compare_data.copy()

        compare_data.update({
            'description': 'This is a test description',
            'customer_id': '1234',
            'assigned_to': AccountTests.user.id,
            'email_addresses': [{
                'email_address': 'test1@account.com',
                'status': 1,
                'status_name': 'Other'
            }],
            'phone_numbers': [{
                'number': '+31612345678',
                'raw_input': '+31612345678',
                'status': 1,
                'status_name': 'Active',
                'type': 'mobile',
                'other_type': None
            }],
            'websites': [{
                'website': 'www.domain.com',
                'is_primary': False
            }],
            'addresses': [
                {
                    'street': 'Street',
                    'street_number': 123,
                    'complement': 'a',
                    'postal_code': '1234AB',
                    'city': 'Somewhere',
                    'country': 'NL',
                    'type': 'visiting',
                    'state_province': ''
                }
            ]
        })

        response = AccountTests.client.post(url, post_data, format='json')

        self.assertGreater(response.data.get('id', 0), 0)
        self.assertGreater(response.data.get('assigned_to', 0), 0)

        del response.data['id']
        del response.data['email_addresses'][0]['id']
        del response.data['phone_numbers'][0]['id']
        del response.data['websites'][0]['id']
        del response.data['addresses'][0]['id']

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, compare_data)

    def test_create_account_with_email_address(self):
        """
        Ensure we can create a new account object with an email address.
        """
        url = reverse('account-list')

        post_data = {
            'name': 'Test account',
            'email_addresses': [{
                'email_address': 'test1@account.com'
            }]
        }

        compare_data = self.default_compare_data.copy()

        compare_data.update({
            'email_addresses': [{
                'email_address': 'test1@account.com',
                'status': 1,
                'status_name': 'Other'
            }],
        })

        response = AccountTests.client.post(url, post_data, format='json')

        self.assertGreater(response.data.get('id', 0), 0)
        del response.data['id']
        del response.data['email_addresses'][0]['id']

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, compare_data)

    def test_patch_account(self):
        """
        Ensure we can update an account.
        """

        account = self.create_account()

        patch_url = reverse('account-detail', kwargs={'pk': account.id})

        patch_data = {
            'name': 'Test account updated'
        }

        compare_data = self.default_compare_data.copy()

        compare_data.update({
            'name': 'Test account updated',
            'description': account.description
        })

        response = AccountTests.client.patch(patch_url, patch_data, format='json')

        self.assertEqual(response.data.get('id', 0), account.id)
        del response.data['id']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, compare_data)

    def test_patch_account_related_fields(self):
        """
        Ensure we can add related field to an existing account.
        """

        account = self.create_account()

        patch_url = reverse('account-detail', kwargs={'pk': account.id})

        patch_data = {
            'email_addresses': [
                {
                    'email_address': 'test1@account.com'
                },
                {
                    'email_address': 'test2@account.com'
                }
            ]
        }

        compare_data = self.default_compare_data.copy()

        compare_data.update({
            'email_addresses': [
                {
                    'email_address': 'test1@account.com',
                    'status': 1,
                    'status_name': 'Other'
                },
                {
                    'email_address': 'test2@account.com',
                    'status': 1,
                    'status_name': 'Other'
                }
            ],
        })

        response = AccountTests.client.patch(patch_url, patch_data, format='json')

        # The data is in a reverse order (order in which it was added?), so reverse the list
        response.data['email_addresses'].reverse()

        self.assertEqual(response.data.get('id', 0), account.id)
        del response.data['id']
        del response.data['email_addresses'][0]['id']
        del response.data['email_addresses'][1]['id']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, compare_data)

    def test_create_account_with_phone_numbers(self):
        """
        Ensure we can create a new account object with phone numbers.
        """
        url = reverse('account-list')

        post_data = {
            'name': 'Test account',
            'phone_numbers': [
                {
                    'raw_input': '0501112222',
                    'type': 'work'
                },
                {
                    'raw_input': '0612345678',
                    'type': 'mobile'
                }
            ]
        }

        compare_data = self.default_compare_data.copy()

        compare_data.update({
            'phone_numbers': [
                {
                    'number': '+31501112222',
                    'raw_input': '+31501112222',
                    'status': 1,
                    'status_name': 'Active',
                    'type': 'work',
                    'other_type': None
                },
                {
                    'number': '+31612345678',
                    'raw_input': '+31612345678',
                    'status': 1,
                    'status_name': 'Active',
                    'type': 'mobile',
                    'other_type': None
                }
            ]
        })

        response = AccountTests.client.post(url, post_data, format='json')

        # The data is in a reverse order (order in which it was added?), so reverse the list
        response.data['phone_numbers'].reverse()

        self.assertGreater(response.data.get('id', 0), 0)
        del response.data['id']
        del response.data['phone_numbers'][0]['id']
        del response.data['phone_numbers'][1]['id']

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, compare_data)

    def test_create_account_with_websites(self):
        """
        Ensure we can create a new account object with websites.
        """
        url = reverse('account-list')

        post_data = {
            'name': 'Test account',
            'websites': [
                {
                    'website': 'domain.com',
                    'is_primary': True
                },
                {
                    'website': 'http://www.otherdomain.com'
                }
            ]
        }

        compare_data = self.default_compare_data.copy()

        compare_data.update({
            'websites': [
                {
                    'website': 'domain.com',
                    'is_primary': True
                },
                {
                    'website': 'http://www.otherdomain.com',
                    'is_primary': False
                }
            ]
        })

        response = AccountTests.client.post(url, post_data, format='json')

        # The data is in a reverse order (order in which it was added?), so reverse the list
        response.data['websites'].reverse()

        self.assertGreater(response.data.get('id', 0), 0)
        del response.data['id']
        del response.data['websites'][0]['id']
        del response.data['websites'][1]['id']

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, compare_data)

    def test_create_account_with_full_address(self):
        """
        Ensure we can create a new account object with a full address.
        """
        url = reverse('account-list')

        post_data = {
            'name': 'Test account',
            'addresses': [
                {
                    'street': 'Street',
                    'street_number': '123',  # Post string on purpose to make sure it gets saved as an integer
                    'complement': 'a',
                    'postal_code': '1234AB',
                    'city': 'Somewhere',
                    'country': 'NL',
                    'type': 'visiting',
                    'state_province': ''
                }
            ]
        }

        compare_data = self.default_compare_data.copy()

        compare_data.update({
            'addresses': [
                {
                    'street': 'Street',
                    'street_number': 123,
                    'complement': 'a',
                    'postal_code': '1234AB',
                    'city': 'Somewhere',
                    'country': 'NL',
                    'type': 'visiting',
                    'state_province': ''
                }
            ]
        })

        response = AccountTests.client.post(url, post_data, format='json')

        self.assertGreater(response.data.get('id', 0), 0)
        del response.data['id']
        del response.data['addresses'][0]['id']

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, compare_data)

    def test_create_account_with_partial_address(self):
        """
        Ensure we can create a new account object with partial data.
        """
        url = reverse('account-list')

        post_data = {
            'name': 'Test account',
            'addresses': [
                {
                    'street': 'Partial Street',
                    'street_number': '123',  # Post string on purpose to make sure it gets saved as an integer
                    'type': 'visiting'
                }
            ]
        }

        compare_data = self.default_compare_data.copy()

        compare_data.update({
            'addresses': [
                {
                    'street': 'Partial Street',
                    'street_number': 123,
                    'complement': None,
                    'postal_code': '',
                    'city': '',
                    'country': '',
                    'type': 'visiting',
                    'state_province': ''
                }
            ]
        })

        response = AccountTests.client.post(url, post_data, format='json')

        self.assertGreater(response.data.get('id', 0), 0)
        del response.data['id']
        del response.data['addresses'][0]['id']

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, compare_data)

    def test_create_account_with_partial_address_2(self):
        """
        Ensure we can create a new account object with other partial data.
        """
        url = reverse('account-list')

        post_data = {
            'name': 'Test account',
            'addresses': [
                {
                    'street': 'Street',
                    'street_number': '123',  # Post string on purpose to make sure it gets saved as an integer
                    'complement': 'a',
                    'country': 'DE',
                    'type': 'visiting',
                }
            ]
        }

        compare_data = self.default_compare_data.copy()

        compare_data.update({
            'addresses': [
                {
                    'street': 'Street',
                    'street_number': 123,
                    'complement': 'a',
                    'postal_code': '',
                    'city': '',
                    'country': 'DE',
                    'type': 'visiting',
                    'state_province': ''
                }
            ]
        })

        response = AccountTests.client.post(url, post_data, format='json')

        self.assertGreater(response.data.get('id', 0), 0)
        del response.data['id']
        del response.data['addresses'][0]['id']

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, compare_data)

    def test_create_account_related_field_error(self):
        """
        Ensure creating an account with an invalid related field produces an error.
        """

        url = reverse('account-list')

        post_data = {
            'name': 'Test account 1',
            'email_addresses': [{'email_address': 'invalidemail'}],
        }

        compare_data = {
            'email_addresses': [{'email_address': ['Enter a valid email address.']}],
        }

        response = AccountTests.client.post(url, post_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, compare_data)

    def test_account_remove_related_field(self):
        """
        Ensure we can remove a related field from an account.
        """

        account = self.create_account({
            'email_addresses': [{'email_address': 'test1@account.com'}, {'email_address': 'test2@account.com'}]
        })

        # Then update the account
        patch_url = reverse('account-detail', kwargs={'pk': account.id})

        patch_data = {
            'email_addresses': [
                {
                    'id': account.email_addresses.first().id,
                    'is_deleted': True
                }
            ]
        }

        compare_data = self.default_compare_data.copy()

        compare_data.update({
            'email_addresses': [
                {
                    'email_address': 'test2@account.com',
                    'status': 1,
                    'status_name': 'Other'
                }
            ],
        })

        response = AccountTests.client.patch(patch_url, patch_data, format='json')

        # The data is in a reverse order (order in which it was added?), so reverse the list
        response.data['email_addresses'].reverse()

        self.assertEqual(response.data.get('id', 0), account.id)
        del response.data['id']
        del response.data['email_addresses'][0]['id']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, compare_data)

    def test_account_remove_non_existant_related_field(self):
        """
        Ensure removing a non-existant related field does nothing.
        """

        account = self.create_account({
            'email_addresses': [{'email_address': 'test1@account.com'}, {'email_address': 'test2@account.com'}]
        })

        # Then update the account
        patch_url = reverse('account-detail', kwargs={'pk': account.id})

        patch_data = {
            'email_addresses': [
                {
                    'id': 99999,
                    'is_deleted': True
                }
            ]
        }

        compare_data = self.default_compare_data.copy()

        compare_data.update({
            'email_addresses': [
                {
                    'email_address': 'test1@account.com',
                    'status': 1,
                    'status_name': 'Other'
                },
                {
                    'email_address': 'test2@account.com',
                    'status': 1,
                    'status_name': 'Other'
                }
            ],
        })

        response = AccountTests.client.patch(patch_url, patch_data, format='json')

        # The data is in a reverse order (order in which it was added?), so reverse the list
        response.data['email_addresses'].reverse()

        self.assertEqual(response.data.get('id', 0), account.id)
        del response.data['id']
        del response.data['email_addresses'][0]['id']
        del response.data['email_addresses'][1]['id']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, compare_data)

    def test_delete_account(self):
        """
        Ensure we can remove an account.
        """
        account = self.create_account()

        delete_url = reverse('account-detail', kwargs={'pk': account.id})

        response = AccountTests.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)

    def test_delete_non_existant_account(self):
        """
        Ensure removing an non-existant account produces an error.
        """
        delete_url = reverse('account-detail', kwargs={'pk': 99999})

        response = AccountTests.client.delete(delete_url)

        compare_data = {
            'detail': 'Not found.'
        }

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, compare_data)
