from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from templated_email import send_templated_mail

from lily.api.fields import DynamicQuerySetPrimaryKeyRelatedField
from lily.api.nested.mixins import RelatedSerializerMixin
from lily.api.nested.serializers import WritableNestedSerializer
from lily.messaging.email.credentials import get_credentials
from lily.users.models import UserInfo

from ..models.models import (EmailLabel, EmailAccount, EmailMessage, Recipient, EmailAttachment, EmailTemplate,
                             SharedEmailConfig, TemplateVariable, DefaultEmailTemplate)
from ..services import GmailService


class SharedEmailConfigSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = SharedEmailConfig
        fields = (
            'id',
            'email_account',
            'is_hidden',
            'privacy',
            'user',
        )


class RelatedSharedEmailConfigSerializer(RelatedSerializerMixin, SharedEmailConfigSerializer):
    pass


class EmailLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLabel
        fields = (
            'id',
            'account',
            'label_type',
            'label_id',
            'name',
            'unread',
        )


class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = (
            'id',
            'name',
            'email_address',
        )


class EmailAttachmentSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source='download_url', read_only=True)

    class Meta:
        model = EmailAttachment
        fields = (
            'id',
            'inline',
            'size',
            'message',
            'cid',
            'name',
            'url',
        )


class EmailMessageSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(read_only=True)
    sender = RecipientSerializer(many=False, read_only=True)
    received_by = RecipientSerializer(many=True, read_only=True)
    received_by_cc = RecipientSerializer(many=True, read_only=True)
    attachments = EmailAttachmentSerializer(many=True, read_only=True)
    labels = EmailLabelSerializer(many=True, read_only=True)
    sent_date = serializers.ReadOnlyField()

    class Meta:
        model = EmailMessage
        fields = (
            'id',
            'account',
            'labels',
            'sent_date',
            'body_html',
            'body_text',
            'received_by',
            'received_by_cc',
            'sender',
            'attachments',
            'read',
            'subject',
            'is_starred',
            'is_spam',
            'is_draft',
            'is_archived',
            'reply_to',
        )


class EmailAccountSerializer(WritableNestedSerializer):
    labels = EmailLabelSerializer(many=True, read_only=True)
    is_public = serializers.BooleanField()
    privacy_display = serializers.CharField(source='get_privacy_display', read_only=True)
    owner = serializers.SerializerMethodField()
    default_template = serializers.SerializerMethodField()
    shared_email_configs = RelatedSharedEmailConfigSerializer(many=True, source='sharedemailconfig_set')

    gmail_service = None

    def validate(self, data):
        validated_data = super(EmailAccountSerializer, self).validate(data)

        request = self.context.get('request')

        if 'only_new' in request.data:
            validated_data.update({
                'only_new': request.data.get('only_new'),
            })

        if self.instance.only_new is None and 'only_new' not in validated_data:
            raise serializers.ValidationError({
                'only_new': [_('Please select one of the email sync options')]
            })

        return validated_data

    def update(self, instance, validated_data):
        user = self.context.get('request').user

        if 'sharedemailconfig_set' in validated_data:
            shared_email_configs = validated_data.pop('sharedemailconfig_set', None)
            initial_configs = self.initial_data.get('shared_email_configs')

            for config in shared_email_configs:
                if config.get('user').id == user.id:
                    raise serializers.ValidationError({
                        'shared_email_configs': _('Can\'t share your email account with yourself')
                    })

                config_id = config.get('id')

                if config_id:
                    for initial_config in initial_configs:
                        if initial_config.get('id') == config_id:
                            shared_config = initial_config

                    if shared_config:
                        shared_config_object = instance.sharedemailconfig_set.get(pk=shared_config.get('id'))

                        if shared_config.get('is_deleted'):
                            shared_config_object.delete()
                        else:
                            shared_config_object.privacy = shared_config.get('privacy')
                            shared_config_object.save()
                else:
                    instance.sharedemailconfig_set.create(**config)

        if not instance.is_authorized or 'only_new' in validated_data:
            # Authorize the email account based on previous stored credentials.
            credentials = get_credentials(instance)
            if credentials:
                instance.is_authorized = True

            # When the user only wants to synchronize only new email messages, retrieve the history id of the email
            # account. That history id is used for the successive (history) sync to retrieve only the changes starting
            # from this moment.
            only_new = validated_data.get('only_new')
            if only_new:
                # Setup service to retrieve history id from Google.
                gmail_service = GmailService(credentials)
                profile = gmail_service.execute_service(gmail_service.service.users().getProfile(userId='me'))

                instance.history_id = profile.get('historyId')
                instance.is_syncing = False

            instance.save()

        if user.info.email_account_status == UserInfo.INCOMPLETE:
            user.info.email_account_status = UserInfo.COMPLETE
            user.info.save()

            # Send an email to the first email account in the tenant.
            if EmailAccount.objects.count() == 1:
                # Get the current site.
                try:
                    current_site = Site.objects.get_current()
                except Site.DoesNotExist:
                    current_site = 'Lily'

                send_templated_mail(
                    template_name='first_impressions',
                    recipient_list=[instance.email_address],
                    context={
                        'current_site': current_site,
                        'first_name': user.first_name,
                    },
                    from_email=settings.EMAIL_PERSONAL_HOST_USER,
                    auth_user=settings.EMAIL_PERSONAL_HOST_USER,
                    auth_password=settings.EMAIL_PERSONAL_HOST_PASSWORD
                )

        return super(EmailAccountSerializer, self).update(instance, validated_data)

    def get_owner(self, obj):
        """
        Using the LilyUserSerializer gives a circular import and thus an error.
        So implement a custom function for the owner of an email account.
        """
        return {
            'id': obj.owner.id,
            'full_name': obj.owner.full_name,
        }

    def get_default_template(self, obj):
        default_template = None

        if self.context:
            user = self.context.get('request').user
            default_template = obj.default_templates.filter(user=user).first()

        return {
            'id': default_template.template.id,
            'name': default_template.template.name,
        } if default_template else None

    class Meta:
        model = EmailAccount
        fields = (
            'id',
            'email_address',
            'from_name',
            'is_syncing',
            'label',
            'labels',
            'is_authorized',
            'is_public',
            'only_new',
            'owner',
            'default_template',
            'privacy',
            'privacy_display',
            'shared_email_configs',
        )
    read_only_fields = ('email_address', 'is_authorized', 'is_syncing', 'is_public',)


class RelatedEmailAccountSerializer(RelatedSerializerMixin, EmailAccountSerializer):
    pass


class EmailTemplateSerializer(serializers.ModelSerializer):
    def get_default_for_queryset(self, instance=None):
        """
        Filtered queryset method that is called for:
            - Fetching of currently related items.
            - Fetching all possible relatable items.

        This function is called once per instance in the list view, and once for the detail view.
        If we're creating a new email template or validating all possible relatable items, instance is None.

        Args:
            instance (EmailTemplate instance): the email template instance for which we want to fetch items.
        """
        if instance:
            queryset = EmailAccount.objects.filter(
                default_templates__template=instance,
                default_templates__user=self.context.get('request').user
            )
        else:
            queryset = EmailAccount.objects.all()
        return queryset

    default_for = DynamicQuerySetPrimaryKeyRelatedField(many=True, queryset=get_default_for_queryset)

    def create(self, validated_data):
        default_for = validated_data.pop('default_for')
        instance = super(EmailTemplateSerializer, self).create(validated_data)

        for email_account_id in default_for:
            # Get defaults for this user for the email account and replace it if exists, if not create new.
            default_template, created = DefaultEmailTemplate.objects.get_or_create(
                account_id=email_account_id,
                user=self.context.get('request').user,
            )
            if created or default_template.template is not instance:
                # Make sure the default is alway this template instance.
                default_template.template = instance
                default_template.save()

        return instance

    def update(self, instance, validated_data):
        user = self.context.get('request').user
        # All email account ids the user submitted through the default_for field.
        validated_account_ids = set([obj.pk for obj in validated_data.pop('default_for', [])])
        # All the email account ids that are in the database, submitted by the user or linked to this template.
        existing_account_ids = set(DefaultEmailTemplate.objects.filter(
            Q(user_id=user.pk),
            Q(account_id__in=validated_account_ids) | Q(template_id=instance.pk)
        ).values_list('account_id', flat=True))

        # Defaults to add are in validated_account_ids but not in existing_account_ids.
        add_list = list(validated_account_ids - existing_account_ids)
        # Defaults to edit are in both validated_account_ids and in existing_account_ids.
        edit_list = list(validated_account_ids & existing_account_ids)
        # Defaults to delete are in existing_account_ids but not in validated_account_ids.
        del_list = list(existing_account_ids - validated_account_ids)

        # Add new default email template relations.
        for add_pk in add_list:
            DefaultEmailTemplate.objects.create(
                user_id=user.pk,
                template_id=instance.pk,
                account_id=add_pk
            )

        # Edit existing email template relations.
        DefaultEmailTemplate.objects.filter(
            user_id=user.pk,
            account_id__in=edit_list
        ).update(
            template_id=instance.pk
        )

        if not self.partial:
            # If not partial then we need to delete the unreferenced default_for relations.
            DefaultEmailTemplate.objects.filter(
                user_id=user.pk,
                template_id=instance.pk,
                account_id__in=del_list
            ).delete()

        return super(EmailTemplateSerializer, self).update(instance, validated_data)

    class Meta:
        model = EmailTemplate
        fields = (
            'id',
            'name',
            'subject',
            'body_html',
            'default_for',
        )


class TemplateVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateVariable
        fields = (
            'id',
            'name',
            'text',
            'is_public',
            'owner',
        )
