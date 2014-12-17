import re
import socket

from django import forms
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.forms import SelectMultiple
from django.forms.models import modelformset_factory
from django.template.defaultfilters import linebreaksbr
from django.utils.translation import ugettext as _
from lily.messaging.models import PRIVATE, SHARED
from lily.contacts.models import Contact
from lily.messaging.utils import get_messages_accounts
from lily.messaging.email.models import (EmailProvider, EmailAccount, EmailTemplate, EmailDraft, EmailAttachment,
    OK_EMAILACCOUNT_AUTH, EmailOutboxAttachment, DefaultEmailTemplate)
from lily.messaging.email.utils import (get_email_parameter_choices, TemplateParser, verify_imap_credentials,
    verify_smtp_credentials)
from lily.messaging.email.forms.widgets import EmailAttachmentWidget
from lily.tenant.middleware import get_current_user
from lily.users.models import LilyUser
from lily.utils.forms import HelloLilyForm, HelloLilyModelForm
from lily.utils.forms.fields import TagsField, HostnameField, FormSetField
from lily.utils.forms.mixins import FormSetFormMixin
from lily.utils.forms.widgets import Wysihtml5Input, AjaxSelect2Widget


class EmailAccountCreateUpdateForm(HelloLilyModelForm):
    preset = forms.ModelChoiceField(
        label=_('Email provider'),
        queryset=EmailProvider.objects.none(),
        empty_label=_('Set a custom email provider'),
        required=False,
    )
    imap_host = HostnameField(max_length=255, label=_('Incoming server (IMAP)'), required=False)
    imap_port = forms.IntegerField(label=_('Incoming port'), required=False)
    imap_ssl = forms.BooleanField(label=_('Incoming SSL'), required=False)
    smtp_host = HostnameField(max_length=255, label=_('Outgoing server (SMTP)'), required=False)
    smtp_port = forms.IntegerField(label=_('Outgoing port'), required=False)
    smtp_ssl = forms.BooleanField(label=_('Outgoing SSL'), required=False)

    def __init__(self, *args, **kwargs):
        self.shared_with = kwargs.pop('shared_with')
        super(EmailAccountCreateUpdateForm, self).__init__(*args, **kwargs)
        self.fields['preset'].queryset = EmailProvider.objects.exclude(name=None)

        if self.instance.pk:
            self.fields['preset'].initial = self.instance.provider

        # With new gmail api this should change, but for now is fine
        self.fields['preset'].initial, created = EmailProvider.objects.get_or_create(
            name='Gmail',
            imap_host='imap.gmail.com',
            imap_port=993,
            imap_ssl=True,
            smtp_host='smtp.gmail.com',
            smtp_port=587,
            smtp_ssl=True,
        )

    def clean(self):
        cleaned_data = super(EmailAccountCreateUpdateForm, self).clean()

        connection_settings_fields = ['imap_host', 'imap_port', 'imap_ssl', 'smtp_host', 'smtp_port', 'smtp_ssl']
        connection_settings = {}

        email = cleaned_data.get('email')
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        preset = cleaned_data.get('preset')

        if preset:
            # A preset is selected, discard what might have been filled in the custom connection settings.
            for setting in connection_settings_fields:
                connection_settings[setting] = getattr(preset, setting)
        else:
            # No preset is selected, use what the user filled in as custom connection settings.
            for setting in connection_settings_fields:
                field_value = cleaned_data.get(setting)

                # For completeness sake always fill the connection_settings dict.
                connection_settings[setting] = field_value

                # If no preset is selected, all the connection settings fields are mandatory.
                if not field_value:
                    self._errors[setting] = self.error_class([_('This field is required.')])

        # Check if the email address is already configured somewhere else.
        try:
            email_account = EmailAccount.objects.get(
                email=email,
                provider__imap_host=connection_settings['imap_host'],
                provider__imap_port=connection_settings['imap_port'],
                provider__imap_ssl=connection_settings['imap_ssl'],
                provider__smtp_host=connection_settings['smtp_host'],
                provider__smtp_port=connection_settings['smtp_port'],
                provider__smtp_ssl=connection_settings['smtp_ssl'],
                is_deleted=False,
            )

            if email_account != self.instance:
                self._errors['email'] = self.error_class(
                    [_('This account already exists, please use sharing options for access by multiple persons.')]
                )
        except EmailAccount.DoesNotExist:
            pass

        if not self.errors:
            # Start verifying when the form has no errors.
            defaulttimeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(4)

            try:
                # Check IMAP
                verify_imap_credentials(
                    connection_settings['imap_host'],
                    connection_settings['imap_port'],
                    connection_settings['imap_ssl'],
                    username,
                    password,
                )
                # Check SMTP
                verify_smtp_credentials(
                    connection_settings['smtp_host'],
                    connection_settings['smtp_port'],
                    connection_settings['smtp_ssl'],
                    username,
                    password,
                )
            except ValidationError:
                raise
            finally:
                socket.setdefaulttimeout(defaulttimeout)

        return cleaned_data

    def save(self, commit=True):
        preset = self.cleaned_data.get('preset')

        try:
            instance = EmailAccount.objects.get(
                email=self.cleaned_data.get('email'),
                provider__imap_host=self.cleaned_data.get('imap_host') or preset.imap_host,
                provider__imap_port=self.cleaned_data.get('imap_port') or preset.imap_port,
                provider__imap_ssl=self.cleaned_data.get('imap_ssl') or preset.imap_ssl,
                provider__smtp_host=self.cleaned_data.get('smtp_host') or preset.smtp_host,
                provider__smtp_port=self.cleaned_data.get('smtp_port') or preset.smtp_port,
                provider__smtp_ssl=self.cleaned_data.get('smtp_ssl') or preset.smtp_ssl,

            )
            instance.is_deleted = False
            instance.password = self.cleaned_data.get('password')
            instance.label = self.cleaned_data.get('label')
        except EmailAccount.DoesNotExist:
            instance = super(EmailAccountCreateUpdateForm, self).save(commit=False)

            if not preset:
                provider, created = EmailProvider.objects.get_or_create(
                    imap_host=self.cleaned_data.get('imap_host'),
                    imap_port=self.cleaned_data.get('imap_port'),
                    imap_ssl=self.cleaned_data.get('imap_ssl'),
                    smtp_host=self.cleaned_data.get('smtp_host'),
                    smtp_port=self.cleaned_data.get('smtp_port'),
                    smtp_ssl=self.cleaned_data.get('smtp_ssl'),
                )
            else:
                provider = preset

            instance.provider = provider
            instance.auth_ok = OK_EMAILACCOUNT_AUTH
            instance.shared_with = self.shared_with
            instance.owner = get_current_user()

        if commit:
            instance.save()

        return instance

    class Meta:
        model = EmailAccount
        fieldsets = (
            (_('Your account'), {
                'fields': ['from_name', 'label', 'email', ],
            }), (_('Account credentials'), {
                'fields': ['username', 'password', 'preset', ],
            }), (_('Connection settings'), {
                'fields': ['imap_host', 'imap_port', 'imap_ssl', 'smtp_host', 'smtp_port', 'smtp_ssl', ],
                'classes': ['hidden', 'advanced_connection_settings'],
            })
        )
        widgets = {
            'password': forms.PasswordInput(),
        }


class EmailAccountShareForm(HelloLilyModelForm):

    user_group = forms.ModelMultipleChoiceField(queryset=LilyUser.objects.none(), label=_('Share with'), required=False, widget=SelectMultiple(attrs={
        'placeholder': _('Select a user'),
    }))

    def __init__(self, *args, **kwargs):
        super(EmailAccountShareForm, self).__init__(*args, **kwargs)
        user = get_current_user()

        self.fields['user_group'].queryset = LilyUser.objects.filter(tenant=user.tenant).exclude(pk=user.pk)
        self.fields['user_group'].help_text = _('To share with everybody create a company email address.')

    def save(self, commit=True):
        instance = super(EmailAccountShareForm, self).save(commit=False)
        if self.cleaned_data.get('user_group'):
            instance.shared_with = SHARED
        else:
            instance.shared_with = PRIVATE

        print instance.pk
        print instance.shared_with

        if commit:
            instance.save()
            self.save_m2m()

        return instance

    class Meta:
        model = EmailAccount


class AttachmentBaseForm(HelloLilyModelForm):
    """
    Form for uploading email attachments.
    """
    class Meta:
        models = EmailOutboxAttachment
        fields = ('attachment',)
        widgets = {
            'attachment': EmailAttachmentWidget(),
        }


class ComposeEmailForm(FormSetFormMixin, HelloLilyModelForm):
    """
    Form for writing an EmailMessage as a draft, reply or forwarded message.
    """
    template = forms.ModelChoiceField(
        label=_('Template'),
        queryset=EmailTemplate.objects,
        empty_label=_('Choose a template'),
        required=False
    )

    send_to_normal = TagsField(
        label=_('To'),
        widget=AjaxSelect2Widget(
            attrs={
                'class': 'tags-ajax'
            },
            url=reverse_lazy('search_view'),
            model=None,
        ),
    )
    send_to_cc = TagsField(
        label=_('Cc'),
        required=False,
        widget=AjaxSelect2Widget(
            attrs={
                'class': 'tags-ajax'
            },
            url=reverse_lazy('search_view'),
            model=None,
        ),
    )
    send_to_bcc = TagsField(
        label=_('Bcc'),
        required=False,
        widget=AjaxSelect2Widget(
            attrs={
                'class': 'tags-ajax'
            },
            url=reverse_lazy('search_view'),
            model=None,
        ),
    )

    attachments = FormSetField(
        queryset=EmailOutboxAttachment.objects,
        formset_class=modelformset_factory(EmailOutboxAttachment, form=AttachmentBaseForm, can_delete=True, extra=0),
        template='email/formset_attachment.html',
    )

    def __init__(self, *args, **kwargs):
        self.draft_id = kwargs.pop('draft_id', None)
        self.message_type = kwargs.pop('message_type', 'reply')
        self.from_contact = kwargs.pop('from_contact', None)
        super(ComposeEmailForm, self).__init__(*args, **kwargs)

        if self.message_type is not 'reply':
            self.fields['attachments'].initial = EmailAttachment.objects.filter(message_id=self.draft_id)

        user = get_current_user()
        email_accounts = get_messages_accounts(user=user, model_cls=EmailAccount)

        # Only provide choices you have access to
        self.fields['send_from'].choices = [(email_account.id, email_account) for email_account in email_accounts]
        self.fields['send_from'].empty_label = None

        # Set user's primary_email as default choice if there is no initial value
        initial_email_account = self.initial.get('send_from', None)
        if not initial_email_account:
            for email_account in email_accounts:
                if email_account.email == user.email:
                    initial_email_account = email_account
        elif isinstance(initial_email_account, basestring):
            for email_account in email_accounts:
                if email_account.email == initial_email_account:
                    initial_email_account = email_account

        self.initial['send_from'] = initial_email_account

    def is_multipart(self):
        """
        Return True since file uploads are possible.
        """
        return True

    def clean(self):
        cleaned_data = super(ComposeEmailForm, self).clean()

        # Make sure at least one of the send_to_X fields is filled in when sending it.
        if 'submit-send' in self.data:
            if not any([cleaned_data.get('send_to_normal'), cleaned_data.get('send_to_cc'), cleaned_data.get('send_to_bcc')]):
                self._errors['send_to_normal'] = self.error_class([_('Please provide at least one recipient.')])

        # Clean send_to addresses.
        cleaned_data['send_to_normal'] = self.format_recipients(cleaned_data.get('send_to_normal'))
        cleaned_data['send_to_cc'] = self.format_recipients(cleaned_data.get('send_to_cc'))
        cleaned_data['send_to_bcc'] = self.format_recipients(cleaned_data.get('send_to_bcc'))

        return cleaned_data

    def format_recipients(self, recipients):
        """
        Strips newlines and trailing spaces & commas from recipients.
        Args:
            recipients (str): The string that needs cleaning up.
        Returns:
            String of comma separated email addresses.
        """
        formatted_recipients = []
        for recipient in recipients:
            # Clean each part of the string
            formatted_recipients.append(recipient.rstrip(', ').strip())

        # Create one string from the parts
        formatted_recipients = ', '.join(formatted_recipients)

        # Regex to split a string by comma while ignoring commas in between quotes
        pattern = re.compile(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''')

        # Split the single string into separate recipients
        formatted_recipients = pattern.split(formatted_recipients)[1::2]

        # It's possible that an extra space is added, so strip it
        formatted_recipients = [recipient.strip() for recipient in formatted_recipients]

        return formatted_recipients

    def clean_send_from(self):
        """
        Verify send_from is a valid account the user has access to.
        """
        cleaned_data = self.cleaned_data
        send_from = cleaned_data.get('send_from')

        email_accounts = get_messages_accounts(user=get_current_user(), model_cls=EmailAccount)
        if send_from.pk not in [account.pk for account in email_accounts]:
            raise ValidationError(
                _('Invalid email account selected to use as sender.'),
                code='invalid',
            )
        else:
            return send_from

    class Meta:
        model = EmailDraft
        fields = ('send_from', 'send_to_normal', 'send_to_cc', 'send_to_bcc', 'subject', 'template', 'body_html',
                  'attachments')
        widgets = {
            'body_html': Wysihtml5Input(),
        }


class CreateUpdateEmailTemplateForm(HelloLilyModelForm):
    """
    Form used for creating and updating email templates.
    """
    variables = forms.ChoiceField(label=_('Insert variable'), choices=[['', 'Select a category']], required=False)
    values = forms.ChoiceField(label=_('Insert value'), choices=[['', 'Select a variable']], required=False)

    def __init__(self, *args, **kwargs):
        """
        Overload super().__init__ to change the appearance of the form and add parameter fields if necessary.
        """
        self.draft_id = kwargs.pop('draft_id', None)
        self.message_type = kwargs.pop('message_type', 'reply')
        super(CreateUpdateEmailTemplateForm, self).__init__(*args, **kwargs)

        email_parameter_choices = get_email_parameter_choices()
        self.fields['variables'].choices += [[x, x] for x in email_parameter_choices.keys()]

        for value in email_parameter_choices:
            for val in email_parameter_choices[value]:
                self.fields['values'].choices += [[val, email_parameter_choices[value][val]], ]

    def clean(self):
        """
        Make sure the form is valid.
        """
        cleaned_data = super(CreateUpdateEmailTemplateForm, self).clean()
        html_part = cleaned_data.get('body_html')
        text_part = cleaned_data.get('body_text')

        if not html_part and not text_part:
            self._errors['body_html'] = self.error_class([_('Please fill in the html part or the text part, at least one of these is required.')])
        elif html_part:
            parsed_template = TemplateParser(html_part)
            if parsed_template.is_valid():
                cleaned_data.update({
                    'body_html': parsed_template.get_text(),
                })
            else:
                self._errors['body_html'] = parsed_template.error.message
                del cleaned_data['body_html']
        elif text_part:
            parsed_template = TemplateParser(text_part)
            if parsed_template.is_valid():
                cleaned_data.update({
                    'body_text': parsed_template.get_text(),
                })
            else:
                self._errors['body_text'] = parsed_template.error.message
                del cleaned_data['body_text']

        return cleaned_data

    def save(self, commit=True):
        instance = super(CreateUpdateEmailTemplateForm, self).save(False)
        instance.body_html = linebreaksbr(instance.body_html.strip())

        if commit:
            instance.save()
        return instance

    class Meta:
        model = EmailTemplate
        fields = ('name', 'subject', 'variables', 'values', 'body_html',)
        widgets = {
            'values': forms.Select(attrs={
                'disabled': 'disabled',
            }),
            'body_html': Wysihtml5Input(),
        }


class EmailTemplateSetDefaultForm(HelloLilyModelForm):
    default_for = forms.ModelMultipleChoiceField(queryset=EmailAccount.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        super(EmailTemplateSetDefaultForm, self).__init__(*args, **kwargs)
        self.fields['default_for'].queryset = get_messages_accounts(user=get_current_user(), model_cls=EmailAccount)

    def save(self, commit=True):
        default_for_data = self.cleaned_data.get('default_for')
        current_user = get_current_user()

        if commit:
            # Only save to db on commit
            for email_account in default_for_data:
                default_template, created = DefaultEmailTemplate.objects.get_or_create(
                    user=current_user,
                    account=email_account,
                    defaults={
                        'template': self.instance,
                    }
                )
                if not created:
                    # If default already exists, override the linked template and set to this one
                    default_template.template = self.instance
                    default_template.save()
            if not default_for_data:
                # There are no accounts submitted, delete previous defaults
                DefaultEmailTemplate.objects.filter(
                    user=current_user,
                    template=self.instance
                ).delete()
            else:
                # Delete defaults that were removed from selection
                account_id_list = []
                default_for_id_list = default_for_data.values_list('pk', flat=True)
                for email_account in self.initial.get('default_for'):
                    if email_account not in default_for_id_list:
                        account_id_list.append(email_account)

                DefaultEmailTemplate.objects.filter(
                    user=current_user,
                    template=self.instance,
                    account_id__in=account_id_list
                ).delete()

        return self.instance

    class Meta:
        model = EmailTemplate
        fieldsets = (
            (_('Set as default for'), {
                'fields': ['default_for', ],
            }),
        )


class EmailTemplateFileForm(HelloLilyForm):
    """
    Form that is used to parse uploaded template files.
    """
    accepted_content_types = ['text/html', 'text/plain']
    body_file = forms.FileField(label=_('Email Template file'))
    default_error_messages = {
        'invalid': _(u'Upload a valid template file. Valid files are: %s.'),
        'syntax': _(u'There was an error in your file:<br> %s'),
    }

    def clean(self):
        """
        Form validation: message body_file should be a valid html file.
        """
        cleaned_data = super(EmailTemplateFileForm, self).clean()
        body_file = cleaned_data.get('body_file', False)

        if body_file:
            if body_file.content_type in self.accepted_content_types:
                parsed_file = TemplateParser(body_file.read().decode('utf-8'))
                if parsed_file.is_valid():
                    # Add body_html to cleaned_data
                    cleaned_data.update(parsed_file.get_parts(default_part='body_html'))
                else:
                    # Syntax error in the template tags/variables
                    self._errors['body_file'] = self.default_error_messages.get('syntax') % parsed_file.error.message
            else:
                # When it doesn't seem like an text/html or text/plain file
                self._errors['body_file'] = self.default_error_messages.get('invalid') % self.accepted_content_types

            del cleaned_data['body_file']
        else:
            # When there is no file at all
            self._errors['body_file'] = self.default_error_messages.get('invalid') % self.accepted_content_types

        return cleaned_data
