from django.utils import timezone
from rest_framework.test import APITestCase

from lily.messaging.email.factories import EmailAccountFactory, EmailMessageFactory
from lily.messaging.email.models.models import EmailMessage, Recipient, EmailLabel, EmailHeader, EmailAccount
from lily.messaging.email.utils import get_filtered_message
from lily.settings import settings
from lily.tenant.factories import TenantFactory
from lily.tests.utils import UserBasedTest
from lily.users.factories import LilyUserFactory


class EmailMessageTests(UserBasedTest, APITestCase):
    """
    Class for unit testing the email message model.
    """

    @classmethod
    def setUpTestData(cls):
        # Create a user, handled by UserBasedTest.
        super(EmailMessageTests, cls).setUpTestData()

        # Create an email account for the user.
        cls.email_account = EmailAccountFactory.create(owner=cls.user_obj, tenant=cls.user_obj.tenant)

        # Create a default recipient
        recipient = Recipient.objects.create(name='Firstname Lastname', email_address='user1@example.com')

        # Create a default email message, initially without any labels.
        cls.email_message = EmailMessage.objects.create(
            account=cls.email_account, sent_date=timezone.now(), sender=recipient
        )

    def test_reply_to(self):
        """
        Test if the reply_to property on the email message returns the email address of the sender.
        """
        self.assertEqual(self.email_message.reply_to, self.email_message.sender.email_address)

    def test_reply_to_header(self):
        """
        Test if the reply_to property on the email message returns the proper address defined by the reply-to header.

        Test with different forms of the reply-to header.
        """
        header = EmailHeader.objects.create(message=self.email_message, name='reply-to', value='user2@example.com')
        self.assertEqual(self.email_message.reply_to, header.value)

        self.email_message.headers.all().delete()
        header = EmailHeader.objects.create(message=self.email_message, name='Reply-To', value='user3@example.com')
        self.assertEqual(self.email_message.reply_to, header.value)

        self.email_message.headers.all().delete()
        header = EmailHeader.objects.create(
            message=self.email_message, name='Reply-To', value='"Firstname Lastname" <user4@example.com>'
        )
        self.assertEqual(self.email_message.reply_to, 'user4@example.com')

        self.email_message.headers.all().delete()
        header = EmailHeader.objects.create(
            message=self.email_message, name='Reply-To', value='Firstname Lastname <user5@example.com>'
        )
        self.assertEqual(self.email_message.reply_to, 'user5@example.com')

    def test_email_message_trashed(self):
        """
        Test if the trashed property is correct with the absence / presence of the trash label.
        """
        # Verify that the email is initially not marked as trash.
        self.assertFalse(self.email_message.is_trashed)

        # Add the trash label.
        self._add_label(settings.GMAIL_LABEL_TRASH)

        # Verify that the email is marked as trashed.
        self.assertTrue(self.email_message.is_trashed)

    def test_email_message_starred(self):
        """
        Test if the starred property is correct with the absence / presence of the star label.
        """
        # Verify that the email is initially not starred.
        self.assertFalse(self.email_message.is_starred)

        # Add the star label.
        self._add_label(settings.GMAIL_LABEL_STAR)

        # Verify that the email is starred.
        self.assertTrue(self.email_message.is_starred)

    def test_email_message_draft(self):
        """
        Test if the draft property is correct with the absence / presence of the draft label.
        """
        # Verify that the email is initially not marked as a draft.
        self.assertFalse(self.email_message.is_draft)

        # Add the draft label.
        self._add_label(settings.GMAIL_LABEL_DRAFT)

        # Verify that the email is marked as a draft.
        self.assertTrue(self.email_message.is_draft)

    def test_email_message_spam(self):
        """
        Test if the spam property is correct with the absence / presence of the spam label.
        """
        # Verify that the email is initially not marked as spam.
        self.assertFalse(self.email_message.is_spam)

        # Add the spam label.
        self._add_label(settings.GMAIL_LABEL_SPAM)

        # Verify that the email is marked as spam.
        self.assertTrue(self.email_message.is_spam)

    def test_email_message_archived(self):
        """
        Test if the archived property is correct with the absence / presence of the inbox label.
        """
        # Verify that the email is initially not archived.
        self.assertTrue(self.email_message.is_archived)

        # Add the inbox label.
        self._add_label(settings.GMAIL_LABEL_INBOX)

        # Verify that the email is not archived.
        self.assertFalse(self.email_message.is_archived)

    def _add_label(self, label):
        # Add the provided label to the email message.
        label = EmailLabel.objects.create(
            account=self.email_account, label_id=label, label_type=EmailLabel.LABEL_SYSTEM
        )
        self.email_message.labels.add(label)


class EmailAccountTests(UserBasedTest, APITestCase):
    def setUp(self):
        # Reset changes made to the email account in a test.
        self.email_account.refresh_from_db()

        self.tenant = TenantFactory.create()
        self.users = LilyUserFactory.create_batch(size=3)
        self.owner = self.users[0]

    @classmethod
    def setUpTestData(cls):
        # Create a user, handled by UserBasedTest.
        super(EmailAccountTests, cls).setUpTestData()

        # Create an email account for the user.
        cls.email_account = EmailAccountFactory.create(owner=cls.user_obj, tenant=cls.user_obj.tenant)

    def test_full_sync_needed_1(self):
        """
        Verify that a full sync on the email account is needed when the history id is missing.
        """
        self.email_account.history_id = None
        self.email_account.sync_failure_count = 0
        self.email_account.is_syncing = False
        self.email_account.save()

        self.assertTrue(self.email_account.full_sync_needed)

    def test_full_sync_needed_2(self):
        """
        Verify that a full sync on the email account is needed when sync failed one time.
        """
        self.email_account.history_id = None
        self.email_account.sync_failure_count = 1
        self.email_account.is_syncing = False
        self.email_account.save()

        self.assertTrue(self.email_account.full_sync_needed)

    def test_full_sync_needed_3(self):
        """
        Verify that a full sync on the email account is needed when sync failed one time.
        """
        self.email_account.history_id = 1
        self.email_account.sync_failure_count = 1
        self.email_account.is_syncing = False
        self.email_account.save()

        self.assertTrue(self.email_account.full_sync_needed)

    def test_full_sync_not_needed_1(self):
        """
        Verify that a full sync on the email account is not needed when the account is syncing at the moment.
        """
        self.email_account.history_id = 1
        self.email_account.sync_failure_count = 0
        self.email_account.is_syncing = True
        self.email_account.save()

        self.assertFalse(self.email_account.full_sync_needed)

    def test_full_sync_not_needed_2(self):
        """
        Verify that a full sync on the email account is not needed when there is a history id and no errors occurred.
        """
        self.email_account.history_id = 1
        self.email_account.sync_failure_count = 0
        self.email_account.is_syncing = False
        self.email_account.save()

        self.assertFalse(self.email_account.full_sync_needed)

    def test_full_sync_not_needed_3(self):
        """
        Verify that a full sync is not needed when the email account is syncing at the moment despite history id is
        missing.
        """
        self.email_account.history_id = None
        self.email_account.sync_failure_count = 0
        self.email_account.is_syncing = True
        self.email_account.save()

        self.assertFalse(self.email_account.full_sync_needed)

    def test_full_sync_not_needed_4(self):
        """
        Verify that a full sync is not needed when the email account is syncing at the moment despite an error occurred
        on the sync.
        """
        self.email_account.history_id = None
        self.email_account.sync_failure_count = 1
        self.email_account.is_syncing = True
        self.email_account.save()

        self.assertFalse(self.email_account.full_sync_needed)

    def test_full_sync_not_needed_5(self):
        """
        Verify that a full sync is not needed when the email account is syncing at the moment despite an error occurred
        on the sync.
        """
        self.email_account.history_id = 1
        self.email_account.sync_failure_count = 1
        self.email_account.is_syncing = True
        self.email_account.save()

        self.assertFalse(self.email_account.full_sync_needed)

    def test_is_public(self):
        """
        Verify that the email account is marked as public.
        """
        self.email_account.privacy = EmailAccount.PUBLIC
        self.email_account.save()

        self.assertTrue(self.email_account.is_public)

    def test_is_public_read_only(self):
        """
        Verify that the email account is not marked as public.
        """
        self.email_account.privacy = EmailAccount.READ_ONLY
        self.email_account.save()

        self.assertFalse(self.email_account.is_public)

    def test_is_public_meta_data(self):
        """
        Verify that the email account is not marked as public.
        """
        self.email_account.privacy = EmailAccount.METADATA
        self.email_account.save()

        self.assertFalse(self.email_account.is_public)

    def test_is_public_private(self):
        """
        Verify that the email account is not marked as public.
        """
        self.email_account.privacy = EmailAccount.PRIVATE
        self.email_account.save()

        self.assertFalse(self.email_account.is_public)

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
