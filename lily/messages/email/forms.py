from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from lily.messages.email.models import EmailAccount, EmailTemplate
from lily.utils.formhelpers import DeleteBackAddSaveFormHelper, LilyFormHelper
from lily.utils.forms import FieldInitFormMixin
from lily.utils.layout import Row


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
    Form for creating an e-mail template.

    """
    body = forms.FileField(label=_('Message body'))

    def __init__(self, *args, **kwargs):
        """
        Overload super().__init__ to change the appearance of the form.

        """
        super(CreateUpdateEmailTemplateForm, self).__init__(*args, **kwargs)

        # Customize form layout
        self.helper = DeleteBackAddSaveFormHelper(form=self)
        self.helper.wrap_by_names(Row, 'name', 'body')

    def clean(self):
        """
        Form validation: message body should be a valid html file.
        """
        cleaned_data = super(CreateUpdateEmailTemplateForm, self).clean()

        #TODO: validate it is a html file that is uploaded.

        return cleaned_data

    class Meta:
        model = EmailTemplate
        fields = ('name', 'body')


class DynamicParameterForm(forms.Form, FieldInitFormMixin):
    def __init__(self, *args, **kwargs):

        # Dynamically set up fields
        for item in range(5):
            self.base_fields['test_field_%s' % item] = forms.CharField(label=_('test_field_%s' % item), max_length=255, required=False, widget=forms.Textarea(attrs={
                'click_and_show': False,
                'class': 'single-line',
            }))

        super(DynamicParameterForm, self).__init__(*args, **kwargs)

        # Customize form layout
        self.helper = LilyFormHelper(form=self)
        self.helper.all().wrap(Row)
