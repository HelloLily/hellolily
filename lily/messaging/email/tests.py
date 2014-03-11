import datetime
from django.test import TestCase
from python_imap.message import Message


class PythonImapTestCase(TestCase):

    def test_test(self):
        data = {
            u'RFC822.SIZE': 72253,
            u'BODY[HEADER.FIELDS (REPLY-TO SUBJECT CONTENT-TYPE TO CC BCC DELIVERED-TO FROM MESSAGE-ID SENDER IN-REPLY-TO RECEIVED DATE)]': u'Delivered-To: bob@voipgrid.nl\r\nReceived: by 10.64.141.67 with SMTP id rm3csp117910ieb; Mon, 10 Mar 2014\r\n 09:53:04 -0700 (PDT)\r\nReceived: from mail-la0-f72.google.com (mail-la0-f72.google.com\r\n [209.85.215.72]) by mx.google.com with ESMTPS id\r\n rl8si18968979lbb.59.2014.03.10.09.53.03 for <bob@voipgrid.nl> (version=TLSv1\r\n cipher=ECDHE-RSA-RC4-SHA bits=128/128); Mon, 10 Mar 2014 09:53:03 -0700 (PDT)\r\nReceived: by mail-la0-f72.google.com with SMTP id gl10sf12592293lab.11 for\r\n <bob@voipgrid.nl>; Mon, 10 Mar 2014 09:53:02 -0700 (PDT)\r\nReceived: by 10.152.23.34 with SMTP id j2ls69072laf.56.gmail; Mon, 10 Mar 2014\r\n 09:53:02 -0700 (PDT)\r\nReceived: from web2k13.voipgrid.osso.nl (partner.voipgrid.nl. [195.35.115.10])\r\n by mx.google.com with ESMTP id c43si35619037eeo.227.2014.03.10.09.53.02 for\r\n <dev@voipgrid.nl>; Mon, 10 Mar 2014 09:53:02 -0700 (PDT)\r\nReceived: by web2k13.voipgrid.osso.nl (Postfix) id 09F64E00125; Mon, 10 Mar\r\n 2014 17:53:02 +0100 (CET)\r\nDelivered-To: commits@web2k13.voipgrid.osso.nl\r\nReceived: by web2k13.voipgrid.osso.nl (Postfix, from userid 0) id 078ACE0115E;\r\n Mon, 10 Mar 2014 17:53:02 +0100 (CET)\r\nTo: commits@web2k13.voipgrid.osso.nl\r\nSubject: [VoIPGRID] Website updated to\r\n 1ff46422462b1b3d49196775b2f345430c51e85c\r\nMessage-Id: <20140310165302.078ACE0115E@web2k13.voipgrid.osso.nl>\r\nDate: Mon, 10 Mar 2014 17:53:02 +0100 (CET)\r\nFrom: root@web2k13.voipgrid.osso.nl (root)\r\n\r\n',
            u'INTERNALDATE': datetime.datetime(2014, 3, 10, 17, 53, 3),
            u'FLAGS': (u'\\Seen',),
            u'SEQ': 423}

        message = Message(data, 1)

        self.assertTrue(False, True)
