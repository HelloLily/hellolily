import time
from django.test import TestCase

from lily.contacts.factories import ContactFactory
from lily.tenant.factories import TenantFactory


class ContactTests(TestCase):
    def test_update_modified(self):
        """
        Test that the modified date of a case gets set properly.
        """
        tenant = TenantFactory.create()
        contact = ContactFactory.create(tenant=tenant)
        modified = contact.modified

        time.sleep(1)

        contact.save(update_modified=False)
        self.assertEqual(modified, contact.modified)

        contact.save(update_modified=True)
        self.assertNotEqual(modified, contact.modified)


