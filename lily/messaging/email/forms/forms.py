import socket

from django import forms
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.forms.models import modelformset_factory
from django.forms.widgets import RadioSelect, SelectMultiple
from django.template.defaultfilters import linebreaksbr
from django.utils.translation import ugettext as _

from lily.contacts.models import Contact
from lily.messaging.email.models import EmailProvider, EmailAccount, EmailTemplate, EmailDraft, EmailAttachment
from lily.messaging.email.utils import get_email_parameter_choices, TemplateParser, verify_imap_credentials, \
    verify_smtp_credentials
from lily.messaging.email.forms.widgets import EmailAttachmentWidget
from lily.tenant.middleware import get_current_user
from lily.users.models import CustomUser
from lily.utils.forms import HelloLilyForm, HelloLilyModelForm
from lily.utils.forms.fields import TagsField, HostnameField, FormSetField
from lily.utils.forms.mixins import FormSetFormMixin
from lily.utils.forms.widgets import ShowHideWidget, BootstrapRadioFieldRenderer, AjaxSelect2Widget
from lily.utils.models import EmailAddress


class EmailConfigurationWizard_1(HelloLilyForm):
    """
    Fields in e-mail configuration wizard step 1.
    """
    email = forms.CharField(max_length=255, label=_('E-mail address'), widget=forms.TextInput(attrs={
        'placeholder': _('email@example.com')
    }))
    username = forms.CharField(max_length=255, label=_('Username'))
    password = forms.CharField(max_length=255, label=_('Password'), widget=forms.PasswordInput())


class EmailConfigurationWizard_2(HelloLilyForm):
    """
    Fields in e-mail configuration wizard step 2.
    """
    preset = forms.ModelChoiceField(
        queryset=EmailProvider.objects,
        empty_label=_('Manually set email server settings'),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(EmailConfigurationWizard_2, self).__init__(*args, **kwargs)

        self.fields['preset'].queryset = EmailProvider.objects.filter(~Q(name=None))


class EmailConfigurationWizard_3(HelloLilyForm):
    """
    Fields in e-mail configuration wizard step 3.
    """
    imap_host = HostnameField(max_length=255, label=_('Incoming server (IMAP)'))
    imap_port = forms.IntegerField(label=_('Incoming port'))
    imap_ssl = forms.BooleanField(label=_('Incoming SSL'), required=False)
    smtp_host = HostnameField(max_length=255, label=_('Outgoing server (SMTP)'))
    smtp_port = forms.IntegerField(label=_('Outgoing port'))
    smtp_ssl = forms.BooleanField(label=_('Outgoing SSL'), required=False)
    share_preset = forms.BooleanField(label=_('Share preset'), required=False)
    preset_name = forms.CharField(max_length=255, label=_('Preset name'), required=False, widget=forms.HiddenInput(),
                                  help_text=_('Entering a name will allow other people in your organisation to use these settings as well'))

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', '')
        self.password = kwargs.pop('password', '')
        self.preset = kwargs.pop('preset', None)

        super(EmailConfigurationWizard_3, self).__init__(*args, **kwargs)

        if self.preset is not None:
            self.fields['share_preset'].widget = forms.HiddenInput()

    def clean(self):
        if hasattr(self, 'preset') and self.preset is not None:
            data = {
                'imap_host': self.preset.imap_host,
                'imap_port': self.preset.imap_port,
                'imap_ssl': self.preset.imap_ssl,
                'smtp_host': self.preset.smtp_host,
                'smtp_port': self.preset.smtp_port,
                'smtp_ssl': self.preset.smtp_ssl
            }
        else:
            data = self.cleaned_data

            if not data['share_preset']:
                # Store name as null/None
                data['preset_name'] = None
            elif data['share_preset']:
                if not data['preset_name'] or data['preset_name'].strip() == '':
                    # If 'Share preset' is checked and preset name is empty, show error
                    msg = _('Preset name can\'t be empty when \'Share preset\' is checked')
                    self._errors['preset_name'] = self.error_class([msg])

        if not self.errors:
            # Start verifying when the form has no errors
            defaulttimeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(2)

            try:
                # Check IMAP
                verify_imap_credentials(
                    data['imap_host'],
                    data['imap_port'],
                    data['imap_ssl'],
                    self.username,
                    self.password,
                )
                # Check SMTP
                verify_smtp_credentials(
                    data['smtp_host'],
                    data['smtp_port'],
                    data['smtp_ssl'],
                    self.username,
                    self.password,
                )
            except:
                raise
            finally:
                socket.setdefaulttimeout(defaulttimeout)

        return data


class EmailConfigurationWizard_4(HelloLilyForm):
    """
    Fields in e-mail configuration wizard step 4.
    """
    name = forms.CharField(max_length=255, label=_('Your name'), widget=forms.TextInput(attrs={
        'placeholder': _('First Last')
    }))
    # signature = forms.CharField(label=_('Your signature'), widget=forms.Textarea(), required=False)


class EmailShareForm(HelloLilyModelForm):
    """
    Form to share an e-mail account.
    """
    def __init__(self, *args, **kwargs):
        """
        Overload super().__init__ to change the appearance of the form.
        """
        self.original_user = kwargs.pop('original_user', None)
        super(EmailShareForm, self).__init__(*args, **kwargs)

        # Exclude original user from queryset when provided
        if self.original_user is not None:
            self.fields['user_group'].queryset = CustomUser.objects.filter(tenant=get_current_user().tenant).exclude(pk=self.original_user.pk)
        else:
            self.fields['user_group'].queryset = CustomUser.objects.filter(tenant=get_current_user().tenant)

        # Overwrite help_text
        self.fields['user_group'].help_text = ''

        # Only a required field when selecting 'Specific users'
        self.fields['user_group'].required = False

    def clean(self):
        """
        Please specify which users to share this email address with.
        """
        cleaned_data = self.cleaned_data

        if cleaned_data.get('shared_with', 0) == 2 and len(cleaned_data.get('user_group', [])) == 0:
            self._errors['user_group'] = self.error_class([_('Please specify which users to share this email address with.')])

        return cleaned_data

    def save(self, commit=True):
        """
        Overloading super().save to at least always add the original user to user_group when provided.
        """
        if self.instance.shared_with < 2:
            # clear relation set for *don't share* and *everybody*
            self.instance.user_group.clear()
        else:
            # save m2m relations properly
            super(EmailShareForm, self).save(commit)

        if self.original_user is not None:
            self.instance.user_group.add(self.original_user)

        self.instance.save()
        return self.instance

    class Meta:
        exclude = (
            'account_type', 'tenant', 'email_account', 'from_name',
            'signature', 'email', 'username', 'password', 'provider',
            'last_sync_date', 'folders', 'auth_ok',
        )
        model = EmailAccount
        widgets = {
            'shared_with': RadioSelect(renderer=BootstrapRadioFieldRenderer, attrs={
                'data-skip-uniform': 'true',
                'data-uniformed': 'true',
            }),
            'user_group': SelectMultiple(attrs={'class': 'chzn-select'})
        }


class AttachmentBaseForm(HelloLilyModelForm):
    """
    Form for uploading email attachments.
    """
    class Meta:
        models = EmailAttachment
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
    send_to_normal = TagsField(label=_('To'))
    send_to_cc = TagsField(required=False, label=_('Cc'))
    send_to_bcc = TagsField(required=False, label=_('Bcc'))
    attachments = FormSetField(
        queryset=EmailAttachment.objects,
        formset_class=modelformset_factory(EmailAttachment, form=AttachmentBaseForm, can_delete=True, extra=0),
        template='email/formset_attachment.html',
    )

    def __init__(self, *args, **kwargs):
        self.draft_id = kwargs.pop('draft_id', None)
        self.message_type = kwargs.pop('message_type', 'reply')
        super(ComposeEmailForm, self).__init__(*args, **kwargs)

        self.fields['attachments'].initial = EmailAttachment.objects.filter(message_id=self.draft_id)

        user = get_current_user()
        email_accounts = user.get_messages_accounts(EmailAccount)

        # Only provide choices you have access to
        self.fields['send_from'].choices = [(email_account.id, email_account) for email_account in email_accounts]
        self.fields['send_from'].empty_label = None

        # Set user's primary_email as default choice if there is no initial value
        initial_email_account = self.initial.get('send_from', None)
        if not initial_email_account:
            for email_account in email_accounts:
                if user.primary_email and email_account.email.email_address == user.primary_email.email_address:
                    initial_email_account = email_account
        elif isinstance(initial_email_account, basestring):
            for email_account in email_accounts:
                if email_account.email.email_address == initial_email_account:
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
                self._errors["send_to_normal"] = self.error_class([_('Please provide at least one recipient.')])

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
            formatted_recipients.append(recipient.rstrip(', '))
        return ', '.join(formatted_recipients)

    def clean_send_from(self):
        """
        Verify send_from is a valid account the user has access to.
        """
        cleaned_data = self.cleaned_data
        send_from = cleaned_data.get('send_from')

        email_accounts = get_current_user().get_messages_accounts(EmailAccount)
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
            'body_html': forms.Textarea(attrs={
                'rows': 12,
                'class': 'inbox-editor inbox-wysihtml5 form-control',
            }),
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
            self._errors['body_html'] = _('Please fill in the html part or the text part, at least one of these is required.')
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
        fields = ('name', 'description', 'subject', 'variables', 'values', 'body_html',)
        widgets = {
            'values': forms.Select(attrs={
                'disabled': 'disabled',
            }),
            'description': ShowHideWidget(forms.Textarea(attrs={
                'rows': 2,
            })),
            'body_html': forms.Textarea(attrs={
                'class': 'inbox-editor inbox-wysihtml5 form-control',
            }),
        }


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


class EmailAccountForm(HelloLilyModelForm):
    """
    Form to change the password for an email account.
    """
    def clean(self):
        """
        Check if connection and login to SMTP client is possible with given data.
        """
        defaulttimeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(2)
        try:
            verify_imap_credentials(
                self.instance.provider.imap_host,
                self.instance.provider.imap_port,
                self.instance.provider.imap_ssl,
                self.cleaned_data['username'],
                self.cleaned_data['password'],
            )
        except:
            raise
        finally:
            socket.setdefaulttimeout(defaulttimeout)

        return self.cleaned_data

    def save(self, commit=True):
        email_account = super(EmailAccountForm, self).save(commit=False)
        email_account.auth_ok = True
        email_account.save()
        return email_account

    class Meta:
        model = EmailAccount
        fields = ('username', 'password')
        widgets = {
            'password': forms.PasswordInput(),
        }
