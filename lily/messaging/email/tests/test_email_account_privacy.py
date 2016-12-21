from django.test import TestCase

from lily.messaging.email.factories import EmailAccountFactory, EmailMessageFactory
from lily.messaging.email.models.models import EmailAccount
from lily.tenant.factories import TenantFactory
from lily.users.factories import LilyUserFactory


class EmailAccountPrivacyTests(TestCase):
    def test_public_account(self):
        """
        Test if having an email account set to public returns all data for everyone.
        """
        tenant = TenantFactory.create()
        users = LilyUserFactory.create_batch(size=3)
        owner = users[0]
        email_account = EmailAccountFactory.create(tenant=tenant, privacy=EmailAccount.PUBLIC, owner=owner)
        email_account.shared_with_users.add(users[1])
        email_messages = EmailMessageFactory.create_batch(account=email_account, size=10)

        for user in users:
            filtered_messages = []

            for email_message in email_messages:
                filtered_message = self.get_filtered_message(email_message, email_account, user)

                if filtered_message:
                    filtered_messages.append(filtered_message)

            self.assertEqual(filtered_messages, email_messages)

    def test_metadata_only(self):
        """
        Test if having an email account set to metadata only returns filtered data for unauthorized users.
        """
        tenant = TenantFactory.create()
        users = LilyUserFactory.create_batch(size=3)
        owner = users[0]
        email_account = EmailAccountFactory.create(tenant=tenant, privacy=EmailAccount.METADATA, owner=owner)
        email_account.shared_with_users.add(users[1])
        email_messages = EmailMessageFactory.create_batch(account=email_account, size=10)

        stripped_messages = []

        for email_message in email_messages:
            stripped_messages.append({
                'sender': email_message.sender.id,
                'subject': email_message.subject,
                'received_by': email_message.received_by.all(),
                'received_by_cc': email_message.received_by_cc.all(),
                'sent_date': email_message.sent_date,
                'account': email_message.account.id,
            })

        for user in users:
            filtered_messages = []

            for email_message in email_messages:
                filtered_message = self.get_filtered_message(email_message, email_account, user)

                if filtered_message:
                    filtered_messages.append(filtered_message)

            if self.has_full_access(email_account, user):
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
        tenant = TenantFactory.create()
        users = LilyUserFactory.create_batch(size=3)
        owner = users[0]
        email_account = EmailAccountFactory.create(tenant=tenant, privacy=EmailAccount.PRIVATE, owner=owner)
        email_account.shared_with_users.add(users[1])
        email_messages = EmailMessageFactory.create_batch(account=email_account, size=10)

        for user in users:
            filtered_messages = []

            for email_message in email_messages:
                filtered_message = self.get_filtered_message(email_message, email_account, user)

                if filtered_message:
                    filtered_messages.append(filtered_message)

            if self.has_full_access(email_account, user):
                self.assertEqual(filtered_messages, email_messages)
            else:
                self.assertEqual(filtered_messages, [])

    def get_filtered_message(self, email_message, email_account, user):
        # Check if the user has full access to the email messages.
        # This means the user is either the owner or the email account has been shared with him/her.
        has_full_access = self.has_full_access(email_account, user)

        # If the email account is set to metadata only, just set these fields.
        if (email_account.privacy == EmailAccount.METADATA and not has_full_access):
            email_message = {
                'sender': email_message.sender,
                'subject': email_message.subject,
                'received_by': email_message.received_by.all(),
                'received_by_cc': email_message.received_by_cc.all(),
                'sent_date': email_message.sent_date,
                'account': email_message.account,
            }
            return email_message
        elif email_account.privacy == EmailAccount.PRIVATE and not has_full_access:
            # Private email (account), so don't add to list.
            return None
        else:
            return email_message

    def has_full_access(self, email_account, user):
        is_owner = email_account.owner == user
        shared_with = (user.id in email_account.shared_with_users.values_list('id', flat=True))

        return (is_owner or shared_with)
