import time
from django.test import TestCase

from lily.accounts.factories import AccountFactory
from lily.tenant.factories import TenantFactory


class AccountTests(TestCase):
    def test_update_modified(self):
        """
        Test that the modified date of a case gets set properly.
        """
        tenant = TenantFactory.create()
        account = AccountFactory.create(tenant=tenant)
        modified = account.modified

        time.sleep(1)

        account.save(update_modified=False)
        self.assertEqual(modified, account.modified)

        account.save(update_modified=True)
        self.assertNotEqual(modified, account.modified)
