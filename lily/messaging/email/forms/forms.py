from email.utils import parseaddr
import logging
import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.core.validators import validate_email
from django.db.models.fields.files import FieldFile
from django.db.models import Q
from django.forms.models import modelformset_factory, ModelForm
from django.template.defaultfilters import linebreaksbr
from django.utils.translation import ugettext_lazy as _

from lily.contacts.models import Contact
from lily.tenant.middleware import get_current_user
from lily.utils.forms.fields import TagsField, FormSetField
from lily.utils.forms.mixins import FormSetFormMixin
from lily.utils.forms.widgets import Wysihtml5Input, AjaxSelect2Widget, BootstrapRadioFieldRenderer

from ..models.models import (EmailAccount, EmailTemplateFolder, EmailTemplate, EmailOutboxAttachment,
                             EmailTemplateAttachment, TemplateVariable, EmailAttachment)
from .widgets import EmailAttachmentWidget
from ..utils import get_email_parameter_choices, TemplateParser, get_shared_email_accounts


logger = logging.getLogger(__name__)


class EmailAccountCreateUpdateForm(ModelForm):

    class Meta:
        model = EmailAccount
        fields = (
            'from_name',
            'label',
            'email_address',
            'privacy',
        )
        widgets = {
            'email_address': forms.TextInput(attrs={'readonly': 'readonly'}),
        }


class AttachmentBaseForm(ModelForm):
    """
    Form for uploading email attachments.
    """
    class Meta:
        models = EmailOutboxAttachment
        fields = ('attachment',)
        widgets = {
            'attachment': EmailAttachmentWidget(),
        }


class ComposeEmailForm(FormSetFormMixin, forms.Form):
    """
    Form for writing an EmailMessage as a draft, reply or forwarded message.
    """
    draft_pk = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    template = forms.ModelChoiceField(
        label=_('Template'),
        queryset=EmailTemplate.objects,
        empty_label=_('Choose a template'),
        required=False
    )

    send_from = forms.ChoiceField()

    send_to_normal = TagsField(
        label=_('To'),
        widget=AjaxSelect2Widget(
            attrs={
                'class': 'tags-ajax'
            },
            url=reverse_lazy('search_view'),
            model=Contact,
            filter_on='contacts_contact',
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
            model=Contact,
            filter_on='contacts_contact',
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
            model=Contact,
            filter_on='contacts_contact',
        ),
    )

    attachments = FormSetField(
        queryset=EmailOutboxAttachment.objects,
        formset_class=modelformset_factory(EmailOutboxAttachment, form=AttachmentBaseForm, can_delete=True, extra=0),
        template='email/formset_attachment.html',
    )

    subject = forms.CharField(required=False, max_length=255)
    body_html = forms.CharField(widget=Wysihtml5Input(), required=False)

    def __init__(self, *args, **kwargs):
        self.message_type = kwargs.pop('message_type', 'reply')
        super(ComposeEmailForm, self).__init__(*args, **kwargs)

        # Only show the checkbox for existing attachments if we have a pk and if we forward.
        if 'initial' in kwargs and 'draft_pk' in kwargs['initial'] and self.message_type == 'forward':
            existing_attachment_list = EmailAttachment.objects.filter(
                message_id=kwargs['initial']['draft_pk'],
                inline=False
            )
            choices = [(attachment.id, attachment.name) for attachment in existing_attachment_list]
            self.fields['existing_attachments'] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple,
                initial=[a.id for a in existing_attachment_list],
                required=False,
            )

        self.fields['template'].queryset = EmailTemplate.objects.order_by('name')

        user = get_current_user()

        email_account_list = get_shared_email_accounts(user)

        self.email_accounts = email_account_list

        # Only provide choices you have access to
        self.fields['send_from'].choices = [(email_account.id, email_account) for email_account in self.email_accounts]
        self.fields['send_from'].empty_label = None

        # Set user's primary_email as default choice if there is no initial value
        initial_email_account = self.initial.get('send_from', None)
        if not initial_email_account:
            if user.primary_email_account:
                initial_email_account = user.primary_email_account.id
            else:
                for email_account in self.email_accounts:
                    if email_account.email_address == user.email:
                        initial_email_account = email_account
                        break
        elif isinstance(initial_email_account, basestring):
            for email_account in self.email_accounts:
                if email_account.email == initial_email_account:
                    initial_email_account = email_account
                    break

        self.initial['send_from'] = initial_email_account

    def is_multipart(self):
        """
        Return True since file uploads are possible.
        """
        return True

    def clean(self):
        cleaned_data = super(ComposeEmailForm, self).clean()

        # Make sure at least one of the send_to_X fields is filled in when sending the email
        if 'submit-send' in self.data:
            if not any([cleaned_data.get('send_to_normal'), cleaned_data.get('send_to_cc'),
                        cleaned_data.get('send_to_bcc')]):
                self._errors['send_to_normal'] = self.error_class([_('Please provide at least one recipient.')])

        # Clean send_to addresses.
        cleaned_data['send_to_normal'] = self.format_recipients(cleaned_data.get('send_to_normal'))
        cleaned_data['send_to_cc'] = self.format_recipients(cleaned_data.get('send_to_cc'))
        cleaned_data['send_to_bcc'] = self.format_recipients(cleaned_data.get('send_to_bcc'))

        for recipient in self.cleaned_data['send_to_normal']:
            email = parseaddr(recipient)[1]
            validate_email(email)

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

        try:
            send_from = int(send_from)
        except ValueError:
            pass
        else:
            try:
                send_from = self.email_accounts.get(pk=send_from)
            except EmailAccount.DoesNotExist:
                raise ValidationError(
                    _('Invalid email account selected to use as sender.'),
                    code='invalid',
                )
            else:
                return send_from

    class Meta:
        fields = (
            'draft_pk',
            'send_from',
            'send_to_normal',
            'send_to_cc',
            'send_to_bcc',
            'subject',
            'template',
            'body_html',
            'attachments',
        )


class CreateUpdateEmailTemplateForm(ModelForm):
    """
    Form used for creating and updating email templates.
    """
    id = forms.IntegerField(label=_('Template ID'), required=False)
    variables = forms.ChoiceField(label=_('Insert variable'), choices=[['', 'Select a category']], required=False)
    values = forms.ChoiceField(label=_('Insert value'), choices=[['', 'Select a variable']], required=False)
    folder = forms.ModelChoiceField(
        label=_('Folder'),
        queryset=EmailTemplateFolder.objects,
        empty_label=_('Choose a folder'),
        required=False
    )

    attachments = FormSetField(
        queryset=EmailTemplateAttachment.objects,
        formset_class=modelformset_factory(EmailTemplateAttachment, form=AttachmentBaseForm, can_delete=True, extra=0),
        template='email/formset_template_attachment.html'
    )

    def __init__(self, *args, **kwargs):
        """
        Overload super().__init__ to change the appearance of the form and add parameter fields if necessary.
        """
        self.draft_id = kwargs.pop('draft_id', None)
        self.message_type = kwargs.pop('message_type', 'reply')
        super(CreateUpdateEmailTemplateForm, self).__init__(*args, **kwargs)

        email_parameter_choices = get_email_parameter_choices()
        self.fields['variables'].choices += [[x, x] for x in email_parameter_choices.keys()]
        self.fields['variables'].choices.append(['Custom variables', 'Custom variables'])

        self.fields['folder'].queryset = EmailTemplateFolder.objects.order_by('name')

        for value in email_parameter_choices:
            for val in email_parameter_choices[value]:
                self.fields['values'].choices += [[val, email_parameter_choices[value][val]], ]

        # Add custom variables to choices
        queryset = TemplateVariable.objects.all().filter(Q(is_public=True) | Q(owner=get_current_user()))

        for template_variable in queryset:
            custom_variable_name = 'custom.' + template_variable.name.lower()

            if template_variable.is_public:
                custom_variable_name += '.public'

            self.fields['values'].choices += [[custom_variable_name, template_variable.name], ]

        if self.instance and self.instance.pk:
            self.fields['id'].widget.attrs['readonly'] = True

        self.fields['attachments'].initial = EmailTemplateAttachment.objects.filter(template_id=self.instance.id)

    def clean(self):
        """
        Make sure the form is valid.
        """
        cleaned_data = super(CreateUpdateEmailTemplateForm, self).clean()
        html_part = cleaned_data.get('body_html')
        text_part = cleaned_data.get('body_text')

        if not html_part and not text_part:
            self._errors['body_html'] = self.error_class(
                [_('Please fill in the html part or the text part, at least one of these is required.')]
            )
        elif html_part:
            # For some reason sometimes nbsp's are added, so remove them
            parsed_template = TemplateParser(self.clean_nbsp(html_part))

            if parsed_template.is_valid():
                cleaned_data.update({
                    'body_html': parsed_template.get_text(),
                })
            else:
                self._errors['body_html'] = parsed_template.error.message
                del cleaned_data['body_html']
        elif text_part:
            # For some reason sometimes nbsp's are added, so remove them
            parsed_template = TemplateParser(self.clean_nbsp(text_part))
            if parsed_template.is_valid():
                cleaned_data.update({
                    'body_text': parsed_template.get_text(),
                })
            else:
                self._errors['body_text'] = parsed_template.error.message
                del cleaned_data['body_text']

        return cleaned_data

    def clean_nbsp(self, text):
        variable_regex = '\[\[&nbsp.+\]\]'
        # Get all template variables that contain an &nbsp;
        search_result = re.findall(variable_regex, text)

        if search_result:
            for template_variable in search_result:
                # Change the nbsp to an actual space
                replace_variable = template_variable.replace('&nbsp;', ' ')
                # Replace the variable in the actual text
                text = re.sub(variable_regex, replace_variable, text)

        return text

    def save(self, commit=True):
        instance = super(CreateUpdateEmailTemplateForm, self).save(False)
        instance.body_html = linebreaksbr(instance.body_html.strip(), autoescape=False)

        if commit:
            instance.save()

        for attachment_form in self.cleaned_data.get('attachments'):
            attachment = attachment_form.cleaned_data.get('attachment', None)

            if attachment:
                if isinstance(attachment, FieldFile) and attachment_form.cleaned_data.get('DELETE'):
                    # We can only delete attachments that exist, so check if it's a new file or an existing file
                    attachment_form.instance.attachment.delete(save=False)
                    attachment_form.instance.delete()
                elif not attachment_form.cleaned_data.get('DELETE'):
                    # If we're not deleting the attachment we can just save it
                    attachment = attachment_form.save(commit=False)
                    attachment.template = instance
                    attachment.save()

        return instance

    def is_multipart(self):
        """
        Return True since file uploads are possible.
        """
        return True

    class Meta:
        model = EmailTemplate
        fields = ('id', 'name', 'subject', 'folder', 'variables', 'values', 'body_html', 'attachments')
        widgets = {
            'values': forms.Select(attrs={
                'disabled': 'disabled',
            }),
            'body_html': Wysihtml5Input(attrs={
                'container_class': 'email-template-body'
            }),
        }


class EmailTemplateFileForm(forms.Form):
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


class CreateUpdateTemplateVariableForm(ModelForm):
    """
    Form used for creating and updating template variables.
    """
    variables = forms.ChoiceField(label=_('Insert variable'), choices=[['', 'Select a category']], required=False)
    values = forms.ChoiceField(label=_('Insert value'), choices=[['', 'Select a variable']], required=False)

    def __init__(self, *args, **kwargs):
        super(CreateUpdateTemplateVariableForm, self).__init__(*args, **kwargs)

        email_parameter_choices = get_email_parameter_choices()
        self.fields['variables'].choices += [[x, x] for x in email_parameter_choices.keys()]

        for value in email_parameter_choices:
            for val in email_parameter_choices[value]:
                self.fields['values'].choices += [[val, email_parameter_choices[value][val]], ]

    def clean(self):
        cleaned_data = super(CreateUpdateTemplateVariableForm, self).clean()

        queryset = TemplateVariable.objects.filter(name__iexact=cleaned_data.get('name'), owner=get_current_user())

        # Check if variable already exists, but only when creating a new one
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exists():
            self._errors['name'] = ['Template variable with that name already exists for this user']

        return cleaned_data

    def save(self, commit=True):
        instance = super(CreateUpdateTemplateVariableForm, self).save(False)

        # Convert \n to <br>
        instance.text = linebreaksbr(instance.text.strip(), autoescape=False)

        if not instance.owner_id:
            instance.owner = get_current_user()

        if commit:
            instance.save()

        return instance

    class Meta:
        model = TemplateVariable
        fields = (
            'id',
            'name',
            'text',
            'is_public',
        )
        widgets = {
            'values': forms.Select(attrs={
                'disabled': 'disabled',
            }),
            'text': Wysihtml5Input(attrs={
                'container_class': 'email-template-body'
            }),
            'is_public': forms.widgets.RadioSelect(renderer=BootstrapRadioFieldRenderer, attrs={
                'data-skip-uniform': 'true',
                'data-uniformed': 'true',
            }),
        }
