from crispy_forms.layout import HTML
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from lily.messages.email.models import EmailAccount, EmailTemplate
from lily.utils.formhelpers import DeleteBackAddSaveFormHelper
from lily.utils.forms import FieldInitFormMixin
from lily.utils.layout import Column, Divider


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


class CreateUpdateEmailTemplateForm(forms.ModelForm, FieldInitFormMixin):
    """
    Form for displaying e-mail parameters.
    """


    def __init__(self, *args, **kwargs):
        """
        Overload super().__init__ to change the appearance of the form and add parameter fields if necessary.
        """
        super(CreateUpdateEmailTemplateForm, self).__init__(*args, **kwargs)
        # Customize form layout
        self.helper = DeleteBackAddSaveFormHelper(form=self)

        self.helper.replace_fields({
            'name': _('Template name*'),
            'description': _('Template description'),
            'subject': _('Subject'),
        }, Column, 4)
        self.helper.replace_fields({
            'body_html': _('Message as HTML'),
            'body_text': _('Message as plain text'),
        }, Column, 8)

        self.helper.insert_after(Divider(), 'subject', )

        body_file_upload = self.helper.create_columns(
            Column(HTML('Type your template below or upload your template file <a href="#" id="body_file_upload" class="body_file_upload" title="upload">here</a>'), size=8, first=True),
            label=''
        )
        self.helper.insert_before(body_file_upload, 'body_html')

    def clean(self):
        cleaned_data = super(CreateUpdateEmailTemplateForm, self).clean()
        html_part = cleaned_data.get('body_html')
        text_part = cleaned_data.get('body_text')

        if not html_part and not text_part:
            self._errors['body_html'] = _('Please fill in the html part or the text part, at least one of these is required.')

        return cleaned_data

    class Meta:
        model = EmailTemplate
        fields = ('name', 'description', 'subject', 'body_html', 'body_text', )
        widgets = {
            'body_html': forms.Textarea(attrs={
                'click_and_show': False,
                })
        }


class EmailTemplateFileForm(forms.Form):
    body_file = forms.FileField(label=_('Message body'))


    def clean(self):
        """
        Form validation: message body_file should be a valid html file.
        """
        valid_formats = ['text/html', 'text/plain']
        cleaned_data = super(EmailTemplateFileForm, self).clean()
        body_file = cleaned_data.get('body_file', False)
        error_msg = "Upload a valid template file. Format can be any of these: %s." % ', '.join(valid_formats)

        if not body_file:
            self._errors["body_file"] = error_msg
        if body_file and not body_file.content_type in valid_formats:
            self._errors["body_file"] = error_msg
            del cleaned_data['body_file']

        return cleaned_data