import datetime
from django.test import TestCase
from python_imap.message import Message


class PythonImapTestCase(TestCase):

    def test_test(self):
        data = {
            u'INTERNALDATE': datetime.datetime(2014, 1, 9, 17, 39, 5),
            u'FLAGS': (u'NotJunk', u'$NotJunk', u'\\Seen'),
            u'SEQ': 1
        }

        message = Message(data, 1)
        import pdb
        pdb.set_trace()

        self.assertTrue(False, True)
