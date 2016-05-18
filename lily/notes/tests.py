import time
from django.test import TestCase

from lily.notes.factories import NoteFactory
from lily.tenant.factories import TenantFactory


class NoteTests(TestCase):
    def test_update_modified(self):
        """
        Test that the modified date of a case gets set properly.
        """
        tenant = TenantFactory.create()
        note = NoteFactory.create(tenant=tenant)
        modified = note.modified

        time.sleep(1)

        note.save(update_modified=False)
        self.assertEqual(modified, note.modified)

        note.save(update_modified=True)
        self.assertNotEqual(modified, note.modified)


