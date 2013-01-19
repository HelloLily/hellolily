from crispy_forms.layout import HTML, Layout, Submit
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.forms import Form, ModelForm
from django.utils.translation import ugettext as _

from lily.messages.email.models import EmailAccount, EmailTemplate, EmailDraft
from lily.messages.email.utils import get_email_parameter_choices, flatten_html_to_text, TemplateParser
from lily.tenant.middleware import get_current_user
from lily.utils.formhelpers import DeleteBackAddSaveFormHelper, LilyFormHelper
from lily.utils.forms import FieldInitFormMixin
from lily.utils.layout import Column, Divider, Button, Row


class CreateUpdateEmailAccountForm(ModelForm):
    password_repeat = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'mws-login-password mws-textinput required',
        'placeholder': _('Password repeat')
    }))

    class Meta:
        model = EmailAccount
        widgets = {
            'provider': forms.Select(attrs={
                'class': 'chzn-select',
            }),
            'name': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Name'),
            }),
            'email': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Email'),
            }),
            'username': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Username'),
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Password'),
            }),
        }


class CreateUpdateEmailTemplateForm(ModelForm, FieldInitFormMixin):
    """
    Form for displaying e-mail parameters.
    """
    variables = forms.ChoiceField(label=_('Insert variable'), choices=[['', 'Select a category']], required=False)
    values = forms.ChoiceField(label=_('Insert value'), choices=[['', 'Select a variable']], required=False)
    text_value = forms.CharField(label=_('Variable'), required=False)
    def __init__(self, *args, **kwargs):
        """
        Overload super().__init__ to change the appearance of the form and add parameter fields if necessary.
        """
        super(CreateUpdateEmailTemplateForm, self).__init__(*args, **kwargs)

        # Customize form layout
        self.helper = DeleteBackAddSaveFormHelper(form=self)
        self.helper.layout = Layout()

        self.helper.add_columns(Column('name', size=4, first=True))
        self.helper.add_columns(Column('description', size=8, first=True))
        self.helper.add_columns(Column('subject', size=4, first=True))

        self.helper.add_columns(
            Column('variables', size=2, first=True),
            Column('values', size=2),
            Column('text_value', size=2),
            Button(name='variable_submit', value=_('Insert'), css_class='small', css_id='id_insert_button'),
            label=_('Insert variable'),
        )

        self.helper.add_columns(Column('body_html', size=8, first=True))
        self.helper.add_columns(Column('body_text', size=8, first=True))

        self.helper.insert_after(Divider(), 'subject', )

        body_file_upload = self.helper.create_columns(
            Column(HTML('Type your template below or upload your template file <a href="#" id="body_file_upload" class="body_file_upload" title="upload">here</a>'), size=8, first=True),
            label=''
        )
        self.helper.insert_before(body_file_upload, 'variables')
        self.fields['variables'].choices += [[x, x] for x in get_email_parameter_choices().keys()]

    def clean(self):
        cleaned_data = super(CreateUpdateEmailTemplateForm, self).clean()
        html_part = cleaned_data.get('body_html')
        text_part = cleaned_data.get('body_text')

        if not html_part and not text_part:
            self._errors['body_html'] = _('Please fill in the html part or the text part, at least one of these is required.')

        return cleaned_data

    class Meta:
        model = EmailTemplate
        fields = ('name', 'description', 'subject', 'variables', 'values', 'text_value', 'body_html', 'body_text', )
        widgets = {
            'values': forms.Select(attrs={
                'disabled': 'disabled',
            }),
            'body_html': forms.Textarea(attrs={
                'placeholder': _('Write your html message body here'),
                'click_and_show': False,
            }),
            'body_text': forms.Textarea(attrs={
                'placeholder': _('Write your plain text message body here'),
            })
        }


class EmailTemplateFileForm(Form):
    body_file = forms.FileField(label=_('Message body'))

    def clean(self):
        """
        Form validation: message body_file should be a valid html file.
        """
        valid_formats = ['text/html', 'text/plain']

        cleaned_data = super(EmailTemplateFileForm, self).clean()
        body_file = cleaned_data.get('body_file', False)
        body_file_type = body_file.content_type

        file_error = '%s %s.' % (_('Upload a valid template file. Format can be any of these:'), ', '.join(valid_formats))
        syntax_error = _('There was an error parsing your template file, please make sure to use correct syntax.')

        if body_file and body_file_type in valid_formats:
            parsed_file = TemplateParser(body_file.read())
            if parsed_file.is_valid():
                default_part = 'html_part' if body_file_type == 'text/html' else 'text_part'
                cleaned_data.update(parsed_file.get_parts(default_part=default_part))
            else:
                self._errors['body_file'] = syntax_error
        else:
            self._errors['body_file'] = file_error

        del cleaned_data['body_file']

        return cleaned_data


class ComposeEmailForm(ModelForm, FieldInitFormMixin):
    """
    Form that lets a user compose an e-mail message.
    """
    # send_from = forms.CharField(label=_('From'), widget=forms.Textarea())
    # send_to_normal = forms.MultiValueField(label=_('To'), required=False)
    # send_to_cc = forms.MultiValueField(label=_('Cc'), required=False)
    # send_to_bcc = forms.MultiValueField(label=_('Bcc'), required=False)
    # subject = forms.CharField(label=_('Subject'))
    # TODO: Insert a formset for attachments?
    model = EmailDraft

    def __init__(self, *args, **kwargs):
        """
        Overload super().__init__ to change the appearance of the form.
        """
        self.draft_id = kwargs.pop('draft_id')
        super(ComposeEmailForm, self).__init__(*args, **kwargs)

        # Customize form layout
        self.helper = LilyFormHelper(form=self)
        self.helper.form_tag = False

        self.helper.all().wrap(Row)
        self.helper.replace('send_from',
            self.helper.create_columns(
                Column('send_from', size=4, first=True),
            ),
        )
        self.helper.replace('subject',
            self.helper.create_columns(
                Column('subject', size=6, first=True),
            ),
        )
        self.helper.replace('send_to_normal',
            self.helper.create_columns(
                Column('send_to_normal', size=6, first=True),
            ),
        )
        self.helper.replace('send_to_cc',
            self.helper.create_columns(
                Column('send_to_cc', size=6, first=True),
            ),
        )
        self.helper.replace('send_to_bcc',
            self.helper.create_columns(
                Column('send_to_bcc', size=6, first=True),
            ),
        )

        if self.draft_id:
            email_template_url = reverse('messages_email_compose_template', kwargs={'pk': self.draft_id})
        else:
            email_template_url = reverse('messages_email_compose_template')

        self.helper.layout.append(
            Row(HTML('<iframe id="email-body" src="%s"></iframe>' % email_template_url))
        )

        self.helper.add_input(Submit('submit-back', _('Back')))
        self.helper.add_input(Submit('submit-discard', _('Discard')))
        self.helper.add_input(Submit('submit-save', _('Save')))
        self.helper.add_input(Submit('submit-send', _('Send')))

        user = get_current_user()
        email_account_ctype = ContentType.objects.get_for_model(EmailAccount)
        email_accounts = EmailAccount.objects.filter(polymorphic_ctype=email_account_ctype, pk__in=user.messages_accounts.values_list('pk')).order_by('name')

        # Filter choices by ctype for EmailAccount
        self.fields['send_from'].empty_label = None
        self.fields['send_from'].choices = [(email_account.pk, email_account.email) for email_account in email_accounts]

        # Set user's primary_email as default choice
        initial_email_account = None
        for email_account in email_accounts:
            if email_account.email == user.primary_email.email_address:
                initial_email_account = email_account
        self.fields['send_from'].initial = initial_email_account

    def clean(self):
        """
        Make sure at least one of the send_to fields is filled in when sending it.
        """
        cleaned_data = super(ComposeEmailForm, self).clean()

        if 'submit-send' in self.data:
            if not any([cleaned_data.get('send_to_normal'), cleaned_data.get('send_to_cc'), cleaned_data.get('send_to_bcc')]):
                raise forms.ValidationError(_('Please provide at least one recipient.'))

        # Clean send_to addresses
        cleaned_data['send_to_normal'] = cleaned_data.get('send_to_normal').rstrip(', ')
        cleaned_data['send_to_cc'] = cleaned_data.get('send_to_cc').rstrip(', ')
        cleaned_data['send_to_bcc'] = cleaned_data.get('send_to_bcc').rstrip(', ')

        return cleaned_data

    def clean_send_from(self):
        """
        Verify send_from is a valid account the user can send from.
        """
        cleaned_data = self.cleaned_data
        send_from = cleaned_data.get('send_from')

        user = get_current_user()
        email_account_ctype = ContentType.objects.get_for_model(EmailAccount)
        email_account_pks = EmailAccount.objects.filter(polymorphic_ctype=email_account_ctype, pk__in=user.messages_accounts.values_list('pk')).values_list('pk', flat=True)

        if send_from.pk not in email_account_pks:
            self._errors['send_from'] = _(u'Invalid email account selected to use as sender.')

        return send_from

    class Meta:
        model = EmailDraft
        fields = ('send_from', 'send_to_normal', 'send_to_cc', 'send_to_bcc', 'subject', 'body')
        widgets = {
            'send_to_normal': forms.Textarea(attrs={
                'placeholder': _('Add recipient'),
                'click_and_show': False,
                'field_classes': 'sent-to-recipients',
            }),
            'send_to_cc': forms.Textarea(attrs={
                'placeholder': _('Add Cc'),
                'click_show_text': _('Add Cc'),
                'field_classes': 'sent-to-recipients',
            }),
            'send_to_bcc': forms.Textarea(attrs={
                'placeholder': _('Add Bcc'),
                'click_show_text': _('Add Bcc'),
                'field_classes': 'sent-to-recipients',
            }),
            'body': forms.HiddenInput()
        }


class ComposeTemplatedEmailForm(ComposeEmailForm):
    """
    Form that lets a user compose an e-mail message based on a template.
    """
    # template = forms.ModelChoiceField(label=_('Template'))
    # template_vars = forms.MultiWidget()
