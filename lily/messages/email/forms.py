# Django imports
from crispy_forms.layout import Submit
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _

# Lily imports
from lily.messages.email.models import EmailAccount, EmailTemplate
from lily.utils.formhelpers import DeleteBackAddSaveFormHelper
from lily.utils.forms import FieldInitFormMixin
from lily.utils.layout import Column, Row, Divider


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

    def __init__(self, parameters=False, *args, **kwargs):
        """
        Overload super().__init__ to change the appearance of the form and add parameter fields if necessary.
        """
        super(CreateUpdateEmailTemplateForm, self).__init__(*args, **kwargs)

        if parameters:
            self.parameter_fields = parameters

            for param in parameters:
                self.fields['%s' % param] = forms.CharField(label=_('default value for %s' % param), max_length=255, required=False, widget=forms.Textarea(attrs={
                    'click_and_show': False,
                    'class': 'single-line',
                    }))

        self.update_fields()

        # Customize form layout
        self.helper = DeleteBackAddSaveFormHelper(form=self)
        self.helper.replace('name',
            self.helper.create_columns(
                Column('name', size=4, first=True),
                label=_('Name*')
            )
        )
        self.helper.replace('body',
            self.helper.create_columns(
                Column('body', size=4, first=True),
                label=_('File*')
            )
        )

        if parameters:
            self.helper.insert_after(Divider, 'body')

            for param in parameters:
                self.helper.replace('%s' % param,
                    self.helper.create_columns(
                        Column('%s' % param, size=4, first=True),
                        label=_('%s' % param)
                    )
                )

    def clean(self):
        """
        Form validation: message body should be a valid html file.
        """
        valid_formats = ['text/html', 'text/plain']
        cleaned_data = super(CreateUpdateEmailTemplateForm, self).clean()
        body = cleaned_data.get('body', False)

        if not body:
            self._errors["body"] = "Upload a valid template file. Format can be any of these: %s." % ', '.join(valid_formats)
        if body and not body.content_type in valid_formats:
            self._errors["body"] = "Upload a valid template file. Format can be any of these: %s." % ', '.join(valid_formats)
            del cleaned_data['body']

        return cleaned_data


    class Meta:
        model = EmailTemplate
        fields = ('name', 'body')


#class DynamicParameterForm(forms.Form, FieldInitFormMixin):
#    def __init__(self, *args, **kwargs):
#
#        # Dynamically set up fields
#        for item in range(5):
#            self.base_fields['test_field_%s' % item] = forms.CharField(label=_('test_field_%s' % item), max_length=255, required=False, widget=forms.Textarea(attrs={
#                'click_and_show': False,
#                'class': 'single-line',
#            }))
#
#        super(DynamicParameterForm, self).__init__(*args, **kwargs)
#
#        # Customize form layout
#        self.helper = LilyFormHelper(form=self)
#        self.helper.all().wrap(Row)
