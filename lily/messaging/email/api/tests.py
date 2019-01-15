import json

from lily.tests.utils import GenericAPITestCase
from lily.messaging.email.factories import (EmailDraftFactory, EmailAccountFactory, EmailMessageFactory,
                                            EmailDraftAttachmentFactory)
from lily.messaging.email.models.models import EmailDraft, EmailAccount, EmailDraftAttachment
from lily.messaging.email.api.serializers import EmailDraftCreateSerializer, EmailDraftAttachmentCreateSerializer
from lily.tenant.middleware import set_current_user, get_current_user

from rest_framework import status
from mock import patch


class DraftEmailTests(GenericAPITestCase):
    """
    Class containing tests for the drafts email API.
    """

    list_url = 'emaildraft-list'
    detail_url = 'emaildraft-detail'
    factory_cls = EmailDraftFactory
    model_cls = EmailDraft
    serializer_cls = EmailDraftCreateSerializer

    def _create_object(self, **kwargs):
        if 'send_from__owner' not in kwargs:
            kwargs['send_from__owner'] = get_current_user()

        return super(DraftEmailTests, self)._create_object(**kwargs)

    def _create_object_stub(self, size=1, action=None, with_send_from=True,
                            with_message=False, **kwargs):
        object_list = super(DraftEmailTests, self)._create_object_stub(size, force_to_list=True, **kwargs)

        for obj in object_list:
            obj['action'] = action or 'compose'  # 'compose' is the default.

            account = EmailAccountFactory(
                owner=self.user_obj,
                tenant=self.user_obj.tenant
            )

            obj['send_from'] = None
            if with_send_from:
                obj['send_from'] = account.id

            if with_message:
                obj['message'] = EmailMessageFactory.create(account=account).id

        if size == 1:
            return object_list[0]

        return object_list

    def _test_create_action_object(self, action, with_send_from=True, with_message=False, should_succeed=True,
                                   with_primary_email_account=True):
        """
        This helper function tests the create functionality for the passed action.
        """
        if with_primary_email_account:
            self.user_obj.primary_email_account = EmailAccountFactory(owner=self.user_obj, tenant=self.user_obj.tenant)
            self.user_obj.save()

        set_current_user(self.user_obj)

        stub_dict = self._create_object_stub(
            action=action,
            with_send_from=with_send_from,
            with_message=with_message
        )

        request = self.user.post(self.get_url(self.list_url), stub_dict)

        if should_succeed:
            self.assertStatus(request, status.HTTP_201_CREATED, stub_dict)
            created_id = json.loads(request.content).get('id')
            self.assertIsNotNone(created_id)

            db_obj = self.model_cls.objects.get(pk=created_id)
            self._compare_objects(db_obj, json.loads(request.content))
        else:
            self.assertStatus(request, status.HTTP_400_BAD_REQUEST, stub_dict)

    def test_create_compose_object(self):
        """
        Test that creating a compose email is possible.
        (is actually also tested by test_create_object_authenticated)
        """
        self._test_create_action_object('compose')

    def test_create_compose_object_with_message(self):
        """
        Test that creating a compose email with a message is not possible.
        """
        self._test_create_action_object('compose', with_message=True, should_succeed=False)

    def test_create_compose_object_without_send_from(self):
        """
        Test that creating a compose email without send_from is possible by falling back on the primary email account.
        """
        self._test_create_action_object('compose', with_send_from=False, should_succeed=True)

    def test_create_compose_object_without_send_from_without_primary_email_account(self):
        """
        Test that creating a compose email without send_from is not possible if there is no primary email account.
        """
        self._test_create_action_object('compose', with_send_from=False, with_primary_email_account=False,
                                        should_succeed=False)

    def test_create_reply_object_with_message(self):
        """
        Test that creating a reply email with message is possible.
        """
        self._test_create_action_object('reply', with_message=True, should_succeed=True)

    def test_create_reply_object_without_message(self):
        """
        Test that creating a reply email without message is not possible.
        """
        self._test_create_action_object('reply', with_message=False, should_succeed=False)

    def test_create_reply_all_object_with_message(self):
        """
        Test that creating a reply-all email with message is possible.
        """
        self._test_create_action_object('reply-all', with_message=True, should_succeed=True)

    def test_create_reply_all_object_without_message(self):
        """
        Test that creating a reply-all email without message is not possible.
        """
        self._test_create_action_object('reply-all', with_message=False, should_succeed=False)

    def test_create_forward_object_with_message(self):
        """
        Test that creating a forward email with message is possible.
        """
        self._test_create_action_object('forward', with_message=True, should_succeed=True)

    def test_create_forward_object_without_message(self):
        """
        Test that creating a forward email without message is not possible.
        """
        self._test_create_action_object('forward', with_message=False, should_succeed=False)

    def test_create_forward_multi_object_with_message(self):
        """
        Test that creating a forward-multi email with message is possible.
        """
        self._test_create_action_object('forward-multi', with_message=True, should_succeed=True)

    def test_create_forward_multi_object_without_message(self):
        """
        Test that creating a forward-multi email without message is not possible.
        """
        self._test_create_action_object('forward-multi', with_message=False, should_succeed=False)

    def test_create_invalid_action_object(self):
        """
        Test that creating an email with an invalid action is not possible.
        """
        self._test_create_action_object('forward-all', with_message=True, should_succeed=False)

    @patch('lily.messaging.email.api.views.get_shared_email_accounts')
    def test__creation_without_available_accounts(self, get_shared_email_accounts_mock):
        """
        Test that creating an email without available accounts is not possible.
        """
        get_shared_email_accounts_mock.return_value = EmailAccount.objects.none()  # we require a queryset

        for action in ['compose', 'reply', 'reply-all', 'forward', 'forward-multi']:
            self._test_create_action_object(action, should_succeed=False)

    @patch('lily.messaging.email.api.views.send_message.delay')
    def test_send_email(self, delay_mock):
        """
        Test that sending an email is possible
        """
        set_current_user(self.user_obj)

        email = self._create_object(size=1)

        self.user.post(self.get_url(self.detail_url, action_name='send', kwargs={'pk': email.pk}))
        self.assertEqual(delay_mock.call_count, 1)


class DraftEmailAttachmentTests(GenericAPITestCase):
    """
    Class containing tests for the drafts email attachments API.
    """

    list_url = 'emaildraftattachment-list'
    detail_url = 'emaildraftattachment-detail'
    factory_cls = EmailDraftAttachmentFactory
    model_cls = EmailDraftAttachment
    serializer_cls = EmailDraftAttachmentCreateSerializer
    ordering = ('-id', )  # Default ordering field.

    def setUp(self):
        email_account = EmailAccountFactory.create(owner=self.user_obj, tenant=self.user_obj.tenant)
        self.email_draft = EmailDraftFactory(tenant=self.user_obj.tenant, send_from=email_account)

    def get_url(self, *args, **kwargs):
        if 'kwargs' not in kwargs:
            kwargs['kwargs'] = dict()

        kwargs['kwargs'].update(draft_id=self.get_or_create_draft().id)

        return super(DraftEmailAttachmentTests, self).get_url(*args, **kwargs)

    def get_or_create_draft(self):
        """
        Both _create_object and get_url require an email draft, while some tests make that only one of these
        functions are called. To simplify, we use this method to return a draft when there isn't one.
        """
        if hasattr(self, 'email_draft'):
            return self.email_draft

        user = get_current_user()
        email_account = EmailAccountFactory.create(owner=user, tenant=user.tenant)
        self.email_draft = EmailDraftFactory(tenant=user.tenant, send_from=email_account)

        return self.email_draft

    def _create_object(self, **kwargs):
        if 'email_draft' not in kwargs:
            kwargs['email_draft'] = self.get_or_create_draft()

        return super(DraftEmailAttachmentTests, self)._create_object(**kwargs)

    def _create_object_stub(self, size=1, **kwargs):
        object_list = super(DraftEmailAttachmentTests, self)._create_object_stub(size, force_to_list=True, **kwargs)

        account = EmailAccountFactory(
            owner=self.user_obj,
            tenant=self.user_obj.tenant
        )

        email_draft = EmailDraftFactory.create(send_from=account)
        for obj in object_list:
            obj['email_draft'] = email_draft.id

            if 'somename' not in obj:
                obj['filename'] = 'theterminator.png'

        if size == 1:
            return object_list[0]

        return object_list

    def test_update_object_unauthenticated(self):
        """ We only create or delete attachments, so the update tests can be skipped. """

    def test_update_object_authenticated(self):
        """ We only create or delete attachments, so the update tests can be skipped. """

    def test_get_list_tenant_filter(self):
        """
        Test that users from different tenants can't access each other's data. First the draft id in the url is
        resolved, when this belongs to another tenant, a 404 is shown instead of an empty list.
        """
        set_current_user(self.other_tenant_user_obj)
        self._create_object(size=3, tenant=self.other_tenant_user_obj.tenant)

        set_current_user(self.user_obj)
        self._create_object(size=3)

        request = self.other_tenant_user.get(self.get_url(self.list_url))

        # The requested page is not found, because the draft belongs to someone else.
        self.assertStatus(request, status.HTTP_404_NOT_FOUND)
