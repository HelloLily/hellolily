import time
from django.test import TestCase

from lily.deals.factories import DealFactory
from lily.tenant.factories import TenantFactory


class DealTests(TestCase):
    def test_update_modified(self):
        """
        Test that the modified date of a case gets set properly.
        """
        tenant = TenantFactory.create()
        deal = DealFactory.create(tenant=tenant)
        modified = deal.modified

        time.sleep(1)

        deal.save(update_modified=False)
        self.assertEqual(modified, deal.modified)

        deal.save(update_modified=True)
        self.assertNotEqual(modified, deal.modified)
