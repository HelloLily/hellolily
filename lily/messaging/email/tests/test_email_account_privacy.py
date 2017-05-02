from django.test import TestCase

from lily.messaging.email.factories import EmailAccountFactory, EmailMessageFactory
from lily.messaging.email.models.models import EmailAccount
from lily.messaging.email.utils import get_filtered_message
from lily.tenant.factories import TenantFactory
from lily.users.factories import LilyUserFactory


class EmailAccountPrivacyTests(TestCase):

    def setUp(self):
        self.tenant = TenantFactory.create()
        self.users = LilyUserFactory.create_batch(size=3)
        self.owner = self.users[0]

    def test_public_account(self):
        """
        Test if having an email account set to public returns all data for everyone.
        """
        email_account = EmailAccountFactory.create(tenant=self.tenant, privacy=EmailAccount.PUBLIC, owner=self.owner)
        # Share the email account with a user.
        config = {
            'user': self.users[1],
            'email_account': email_account,
            'privacy': EmailAccount.PUBLIC,
            'tenant': self.tenant,
        }
        email_account.sharedemailconfig_set.create(**config)

        email_messages = EmailMessageFactory.create_batch(account=email_account, size=10)

        for user in self.users:
            filtered_messages = []

            for email_message in email_messages:
                filtered_message = get_filtered_message(email_message, email_account, user)

                if filtered_message:
                    filtered_messages.append(filtered_message)

            self.assertEqual(filtered_messages, email_messages)

    def test_metadata_only(self):
        """
        Test if having an email account set to metadata only returns filtered data for unauthorized users.
        """
        email_account = EmailAccountFactory.create(tenant=self.tenant, privacy=EmailAccount.METADATA, owner=self.owner)
        # Share the email account with a user.
        config = {
            'user': self.users[1],
            'email_account': email_account,
            'privacy': EmailAccount.PUBLIC,
            'tenant': self.tenant,
        }
        email_account.sharedemailconfig_set.create(**config)

        email_messages = EmailMessageFactory.create_batch(account=email_account, size=10)

        stripped_messages = []

        for email_message in email_messages:
            stripped_messages.append({
                'id': email_message.id,
                'sender': email_message.sender,
                'received_by': email_message.received_by.all(),
                'received_by_cc': email_message.received_by_cc.all(),
                'sent_date': email_message.sent_date,
                'account': email_message.account,
            })

        for user in self.users:
            filtered_messages = []

            for email_message in email_messages:
                filtered_message = get_filtered_message(email_message, email_account, user)

                if filtered_message:
                    filtered_messages.append(filtered_message)

            if self._can_view_full_message(email_account, user):
                self.assertEqual(filtered_messages, email_messages)
            else:
                # Comparing lists of dicts doesn't seem to work properly.
                # So loop through all filter and stripped messages and compare them.
                for i in range(len(filtered_messages)):
                    self.assertItemsEqual(filtered_messages[i], stripped_messages[i])

    def test_private_account(self):
        """
        Test if having an email account set to private returns no data for unauthorized users.
        """
        email_account = EmailAccountFactory.create(tenant=self.tenant, privacy=EmailAccount.PRIVATE, owner=self.owner)
        # Share the email account with a user.
        config = {
            'user': self.users[1],
            'email_account': email_account,
            'privacy': EmailAccount.PUBLIC,
            'tenant': self.tenant,
        }
        email_account.sharedemailconfig_set.create(**config)

        email_messages = EmailMessageFactory.create_batch(account=email_account, size=10)

        for user in self.users:
            filtered_messages = []

            for email_message in email_messages:
                filtered_message = get_filtered_message(email_message, email_account, user)

                if filtered_message:
                    filtered_messages.append(filtered_message)

            if self._can_view_full_message(email_account, user):
                self.assertEqual(filtered_messages, email_messages)
            else:
                self.assertEqual(filtered_messages, [])

    def _can_view_full_message(self, email_account, user):
        shared_config = email_account.sharedemailconfig_set.filter(user=user).first()

        if email_account.owner == user:
            return True
        elif shared_config:
            if shared_config.privacy == EmailAccount.PUBLIC or shared_config.privacy == EmailAccount.READ_ONLY:
                return True
            elif email_account.privacy == EmailAccount.PUBLIC or email_account.privacy == EmailAccount.READ_ONLY:
                return True

        return False
