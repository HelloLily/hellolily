import time
from django.test import TestCase

from lily.cases.factories import CaseFactory
from lily.tenant.factories import TenantFactory


class CaseTests(TestCase):
    def test_update_modified(self):
        """
        Test that the modified date of a case gets set properly.
        """
        tenant = TenantFactory.create()
        case = CaseFactory.create(tenant=tenant)
        modified = case.modified

        time.sleep(1)

        case.save(update_modified=False)
        self.assertEqual(modified, case.modified)

        case.save(update_modified=True)
        self.assertNotEqual(modified, case.modified)
