from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from oauth2client.contrib.django_orm import Storage
from rest_framework import serializers

from lily.api.fields import DynamicQuerySetPrimaryKeyRelatedField
from lily.api.nested.mixins import RelatedSerializerMixin
from lily.users.models import UserInfo

from ..models.models import (EmailLabel, EmailAccount, EmailMessage, Recipient, EmailAttachment, EmailTemplate,
                             SharedEmailConfig, TemplateVariable, DefaultEmailTemplate, GmailCredentialsModel)
from ..services import build_gmail_service


class SharedEmailConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedEmailConfig
        fields = ('id', 'email_account', 'is_hidden')


class EmailLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLabel
        fields = ('id', 'account', 'label_type', 'label_id', 'name', 'unread')


class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = ('id', 'name', 'email_address')


class EmailAttachmentSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source='download_url', read_only=True)

    class Meta:
        model = EmailAttachment
        fields = ('id', 'inline', 'size', 'message', 'cid', 'name', 'url', )


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


class EmailAccountSerializer(serializers.ModelSerializer):
    labels = EmailLabelSerializer(many=True, read_only=True)
    is_public = serializers.BooleanField()
    privacy_display = serializers.CharField(source='get_privacy_display', read_only=True)
    owner = serializers.SerializerMethodField()
    default_template = serializers.SerializerMethodField()

    def validate(self, data):
        validated_data = super(EmailAccountSerializer, self).validate(data)

        request = self.context.get('request')

        if 'only_new' in request.data:
            validated_data.update({
                'only_new': request.data.get('only_new'),
            })

        return validated_data

    def update(self, instance, validated_data):
        user = self.context.get('request').user
        shared_with_users = validated_data.get('shared_with_users')

        if shared_with_users:
            instance.shared_with_users.clear()
            instance.save()

            for shared_with_user in shared_with_users:
                if shared_with_user.id == user.id:
                    raise serializers.ValidationError({
                        'shared_with_users': _('Can\'t share your email account with yourself')
                    })

                instance.shared_with_users.add(shared_with_user)

        if not instance.is_authorized or 'only_new' in validated_data:
            only_new = validated_data.get('only_new')
            # Store credentials based on new email account.
            storage = Storage(GmailCredentialsModel, 'id', instance, 'credentials')
            credentials = storage.get()

            # Setup service to retrieve email address.
            service = build_gmail_service(credentials)
            profile = service.users().getProfile(userId='me').execute()

            if credentials:
                instance.is_authorized = True

            if only_new:
                instance.history_id = profile.get('historyId')
                instance.full_sync_finished = True

            instance.save()

        if user.info.email_account_status == UserInfo.INCOMPLETE:
            user.info.email_account_status = UserInfo.COMPLETE
            user.info.save()

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
            'full_sync_finished',
            'label',
            'labels',
            'is_authorized',
            'is_public',
            'owner',
            'default_template',
            'privacy',
            'privacy_display',
            'shared_with_users',
        )
    read_only_fields = ('email_address', 'is_authorized', 'full_sync_finished', 'is_public',)


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
