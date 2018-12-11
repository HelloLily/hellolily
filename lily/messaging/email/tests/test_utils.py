from django.test import TestCase

from lily.messaging.email.utils import get_formatted_email_body, get_formatted_reply_email_subject
from lily.tests.utils import UserBasedTest, EmailBasedTest


class EmailUtilsTestCase(UserBasedTest, EmailBasedTest, TestCase):
    def setUp(self):
        super(EmailUtilsTestCase, self).setUp()
        super(EmailUtilsTestCase, self).setupEmailMessage()

    def get_expected_email_body_parts(self, subject='Simple Subject',
                                      recipient='Simple Name &lt;someuser@example.com&gt;'):
        expected_body_html_part_one = (
            '<br /><br /><hr />---------- Forwarded message ---------- <br />'
            'From: user1@example.com<br/>'
            'Date: '
        )
        expected_body_html_part_two = (
            '<br/>Subject: ' + subject + '<br/>'
            'To: ' + recipient + '<br />'
        )

        return expected_body_html_part_one.encode('utf-8'), expected_body_html_part_two.encode('utf-8')

    def test_get_formatted_email_body_action_forward(self):
        body_html = get_formatted_email_body('forward', self.email_message)

        part_one, part_two = self.get_expected_email_body_parts()

        self.assertIn(part_one, body_html)
        self.assertIn(part_two, body_html)

    def test_get_formatted_email_body_action_forward_complex_subject(self):
        self.email_message.subject = 'Complex S' u'\u2265' 'bject'
        body_html = get_formatted_email_body('forward', self.email_message)

        part_one, part_two = self.get_expected_email_body_parts(self.email_message.subject)

        self.assertIn(part_one, body_html)
        self.assertIn(part_two, body_html)

    def test_get_formatted_email_body_action_forward_complex_recipient(self):
        received_by = self.email_message.received_by.first()
        received_by.name = 'C' u'\u2265' 'mplicated Name'
        received_by.save()
        body_html = get_formatted_email_body('forward', self.email_message)

        recipient = 'C' u'\u2265' 'mplicated Name &lt;someuser@example.com&gt;'
        part_one, part_two = self.get_expected_email_body_parts(recipient=recipient)

        self.assertIn(part_one, body_html)
        self.assertIn(part_two, body_html)

    def test_get_formatted_email_body_action_forward_simple(self):
        self.email_message.subject = 'Simple Subject'
        received_by = self.email_message.received_by.first()
        received_by.name = None
        received_by.email_address = 'support@' u'\u2265' 'mail.nl'
        received_by.save()

        body_html = get_formatted_email_body('forward', self.email_message)

        part_one, part_two = self.get_expected_email_body_parts(recipient=received_by.email_address)

        self.assertIn(part_one, body_html)
        self.assertIn(part_two, body_html)

    def test_get_formatted_reply_email_subject(self):
        subject = get_formatted_reply_email_subject(u'\u2265')
        self.assertEqual('Re: {}'.format(u'\u2265'.encode('utf-8')), subject)
