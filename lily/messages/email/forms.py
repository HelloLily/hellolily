# Django imports
from crispy_forms.layout import Submit
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _

# Lily imports
from lily.messages.email.models import EmailAccount, EmailTemplate, EmailTemplateParameterChoice
from lily.messages.email.utils import parse
from lily.utils.formhelpers import DeleteBackAddSaveFormHelper, LilyFormHelper
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


class TemplateParameterMixin(FieldInitFormMixin):
    """
    Mixin that adds two functions for easy parameter fields generating.

    """
    def add_parameter_fields(self, parameters, choice_list):
        if not any(choice[0] == '' for choice in choice_list):
            choice_list.insert(0, ['', _('Static value')])

        if isinstance(parameters, dict):
            for param in parameters:
                self.fields['%s_select' % param] = forms.ChoiceField(
                    required=False,
                    choices=choice_list,
                    default='',
                    widget=forms.Select(attrs={
                        'class': 'param-select',
                    })
                )
                self.fields['%s_input' % param] = forms.CharField(
                    label=_('default value for %s' % param),
                    max_length=255, required=False,
                    initial=parameters[param],
                    widget=forms.Textarea(attrs={
                        'click_and_show': False,
                        'class': 'single-line',
                    })
                )
        else:
            for param in parameters:
                self.fields['%s_select' % param] = forms.ChoiceField(
                    required=False,
                    choices=choice_list,
                    widget=forms.Select(attrs={
                        'class': 'param-select',
                    })
                )
                self.fields['%s_input' % param] = forms.CharField(
                    label=_('default value for %s' % param),
                    max_length=255,
                    required=False,
                    widget=forms.Textarea(attrs={
                        'click_and_show': False,
                        'class': 'single-line',
                    })
                )

        # Fix CSS for newly added fields
        self.update_fields()


    def wrap_parameter_fields(self, parameters, helper):
        for param in parameters:
            helper.remove('%s_select' % param)
            helper.replace('%s_input' % param,
                helper.create_columns(
                    Column('%s_select' % param, size=4, first=True),
                    Column('%s_input' % param, size=4, first=False),
                    label=_('%s' % param)
                )
            )


class TemplateParameterForm(ModelForm, TemplateParameterMixin):
    """
    Form for displaying e-mail parameters.
    """
    def __init__(self, parameters, *args, **kwargs):
        """
        Overload super().__init__ to change the appearance of the form and add parameter fields if necessary.
        """
        super(TemplateParameterForm, self).__init__(*args, **kwargs)

        choice_list = [[choice.value, choice.label] for choice in EmailTemplateParameterChoice.objects.all()]
        self.add_parameter_fields(parameters, choice_list)

        self.helper = LilyFormHelper(form=self)
        self.helper.layout.insert(0, Divider())

        self.wrap_parameter_fields(parameters, self.helper)


    class Meta:
        model = EmailTemplate
        fields = ()


class TemplateParameterParseForm(ModelForm):
    """
    Form used while parsing an e-mail template.
    """
    body = forms.FileField(label=_('Message body'))


    def clean(self):
        """
        Form validation: message body should be a valid html file.
        """
        valid_formats = ['text/html', 'text/plain']
        cleaned_data = super(TemplateParameterParseForm, self).clean()
        body = cleaned_data.get('body', False)

        if not body:
            self._errors["body"] = "Upload a valid template file. Format can be any of these: %s." % ', '.join(valid_formats)
        if body and not body.content_type in valid_formats:
            self._errors["body"] = "Upload a valid template file. Format can be any of these: %s." % ', '.join(valid_formats)
            del cleaned_data['body']

        return cleaned_data


    class Meta:
        model = EmailTemplate
        fields = ('body', )


class CreateUpdateEmailTemplateForm(TemplateParameterParseForm, TemplateParameterMixin):
    """
    Form for creating an e-mail template.

    """
    def __init__(self, parameters=None,  *args, **kwargs):
        """
        Overload super().__init__ to change the appearance of the form and add parameter fields if necessary.
        """
        super(CreateUpdateEmailTemplateForm, self).__init__(*args, **kwargs)

        if parameters:
            choice_list = [[choice.value, choice.label] for choice in EmailTemplateParameterChoice.objects.all()]
            self.add_parameter_fields(parameters, choice_list)

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
            self.wrap_parameter_fields(parameters, self.helper)


    def clean(self):
        cleaned_data = super(CreateUpdateEmailTemplateForm, self).clean()
        body = cleaned_data.get('body')

        if body:
            self.parameter_list = parse(body.read())

            for key in cleaned_data.keys():
                if key not in self.base_fields.keys() and key not in self.parameter_list:
                    del cleaned_data[key]

        return cleaned_data


    class Meta:
        model = EmailTemplate
        fields = ('name', 'body')