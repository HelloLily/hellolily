import socket
import traceback
from smtplib import SMTPAuthenticationError
from urlparse import urlparse

from crispy_forms.layout import HTML, Layout, Submit
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.forms import Form, ModelForm
from django.template.defaultfilters import linebreaksbr
from django.utils.translation import ugettext as _

from lily.messaging.email.emailclient import LilyIMAP
from lily.messaging.email.models import EmailProvider, EmailAccount, EmailTemplate, EmailDraft
from lily.messaging.email.utils import get_email_parameter_choices, TemplateParser
from lily.tenant.middleware import get_current_user
from lily.utils.fields import EmailProviderChoiceField
from lily.utils.formhelpers import DeleteBackAddSaveFormHelper, LilyFormHelper
from lily.utils.forms import FieldInitFormMixin
from lily.utils.layout import Column, Divider, Button, Row
from lily.utils.widgets import EmailProviderSelect


class CreateUpdateEmailTemplateForm(ModelForm, FieldInitFormMixin):
    """
    Form used for creating and updating email templates.
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
            Button(name='variable_submit', value=_('Insert'), css_id='id_insert_button'),
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
    """
    Form that is used to parse uploaded template files.
    """
    body_file = forms.FileField(label=_('Message body'))

    def clean(self):
        """
        Form validation: message body_file should be a valid html file.
        """
        valid_formats = ['text/html', 'text/plain']

        cleaned_data = super(EmailTemplateFileForm, self).clean()
        body_file = cleaned_data.get('body_file', False)

        file_error = '%s %s.' % (_('Upload a valid template file. Format can be any of these:'), ', '.join(valid_formats))
        syntax_error = _('There was an error parsing your template file:')

        if body_file:
            body_file_type = body_file.content_type
            if body_file_type in valid_formats:
                parsed_file = TemplateParser(body_file.read().decode('utf-8'))
                if parsed_file.is_valid():
                    default_part = 'html_part' if body_file_type == 'text/html' else 'text_part'
                    cleaned_data.update(parsed_file.get_parts(default_part=default_part))
                else:
                    self._errors['body_file'] = syntax_error + ' "' + parsed_file.error.message + '"'
            else:
                self._errors['body_file'] = file_error
            del cleaned_data['body_file']
        else:
            self._errors['body_file'] = file_error

        return cleaned_data


class ComposeEmailForm(ModelForm, FieldInitFormMixin):
    """
    Form that lets a user compose an e-mail message.
    """
    template = forms.ModelChoiceField(label=_('Template'), queryset=EmailTemplate.objects.all(), empty_label=_('Choose a template'))

    # TODO: Insert a formset for attachments?
    def __init__(self, *args, **kwargs):
        """
        Overload super().__init__ to change the appearance of the form.
        """
        self.draft_id = kwargs.pop('draft_id', None)
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
            email_template_url = reverse('messaging_email_compose_template', kwargs={'pk': self.draft_id})
        else:
            email_template_url = reverse('messaging_email_compose_template')

        self.helper.layout.append(
            Row(HTML('<iframe id="email-body" src="%s"></iframe>' % email_template_url))
        )

        self.helper.add_input(Submit('submit-back', _('Back')))
        self.helper.add_input(Submit('submit-discard', _('Discard')))
        self.helper.add_input(Submit('submit-save', _('Save')))
        self.helper.add_input(Submit('submit-send', _('Send')))

        user = get_current_user()
        email_account_ctype = ContentType.objects.get_for_model(EmailAccount)
        email_accounts = EmailAccount.objects.filter(polymorphic_ctype=email_account_ctype, pk__in=user.messages_accounts.values_list('pk')).order_by('email__email_address')

        # Filter choices by ctype for EmailAccount
        self.fields['send_from'].empty_label = None
        self.fields['send_from'].choices = [(email_account.pk, '"%s" <%s>' % (email_account.from_name, email_account.email.email_address)) for email_account in email_accounts]

        # Set user's primary_email as default choice if no initial was provided
        initial_email_account = None
        for email_account in email_accounts:
            if self.initial.get('send_from', None) not in [None, '']:
                if email_account.email == self.initial.get('send_from'):
                    initial_email_account = email_account
            elif email_account.email == user.primary_email.email_address:
                initial_email_account = email_account
        self.initial['send_from'] = initial_email_account

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
        fields = ('send_from', 'send_to_normal', 'send_to_cc', 'send_to_bcc', 'subject', 'template', 'body')
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


class EmailConfigurationStep1Form(Form, FieldInitFormMixin):
    """
    Fields in e-mail configuration wizard step 1.
    """
    email = forms.CharField(max_length=255, label=_('E-mail address'), widget=forms.TextInput(attrs={
        'placeholder': _('email@example.com')
    }))
    username = forms.CharField(max_length=255, label=_('Username'))
    password = forms.CharField(max_length=255, label=_('Password'), widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(EmailConfigurationStep1Form, self).__init__(*args, **kwargs)


class EmailConfigurationStep2Form(Form, FieldInitFormMixin):
    """
    Fields in e-mail configuration wizard step 2.
    """
    presets = EmailProviderChoiceField(queryset=EmailProvider.objects.none(), widget=EmailProviderSelect(attrs={
        'class': 'chzn-select-no-search'
    }), required=False)
    imap_host = forms.URLField(max_length=255, label=_('Incoming server (IMAP)'))
    imap_port = forms.IntegerField(label=_('Incoming port'))
    imap_ssl = forms.BooleanField(label=_('Incoming SSL'), required=False)
    smtp_host = forms.URLField(max_length=255, label=_('Outgoing server (SMTP)'))
    smtp_port = forms.IntegerField(label=_('Outgoing port'))
    smtp_ssl = forms.BooleanField(label=_('Outgoing SSL'), required=False)

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', '')
        self.password = kwargs.pop('password', '')
        super(EmailConfigurationStep2Form, self).__init__(*args, **kwargs)

        self.fields['presets'].queryset = EmailProvider.objects.all()

    def clean(self):
        data = self.cleaned_data
        if data.get('imap_host', None) is not None:
            data['imap_host'] = urlparse(data.get('imap_host')).netloc

        if data.get('smtp_host', None) is not None:
            data['smtp_host'] = urlparse(data.get('smtp_host')).netloc

        if not self.errors:
            # Start verifying when the form has no errors
            defaulttimeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(1)

            try:
                imap_host = data.get('imap_host')
                try:
                    # Resolve host name
                    socket.gethostbyname(imap_host)
                except Exception, e:
                    print traceback.format_exc(e)
                    raise forms.ValidationError(_('Could not resolve %s' % imap_host))
                else:
                    try:
                        # Try connecting
                        imap = LilyIMAP(ssl=data.get('imap_ssl'), test=True, host=imap_host, port=int(data.get('imap_port')), username=self.username, password=self.password)
                        imap_client = imap._get_imap_client()
                        if not imap_client:
                            raise forms.ValidationError(_('Could not connect to %s:%s' % (imap_host, data.get('imap_port'))))
                    except Exception, e:
                        print traceback.format_exc(e)
                        raise forms.ValidationError(_('Could not connect to %s:%s' % (imap_host, data.get('imap_port'))))
                    else:
                        try:
                            # Try authenticating
                            server = imap._login_in_imap(imap_client)
                            if not server:
                                raise forms.ValidationError(_('Unable to login with provided username and password on the IMAP host'))
                        except Exception, e:
                            print traceback.format_exc(e)
                            raise forms.ValidationError(_('Unable to login with provided username and password on the IMAP host'))

                smtp_host = data.get('smtp_host')
                try:
                    # Resolve SMTP server
                    socket.gethostbyname(smtp_host)
                except Exception, e:
                    raise forms.ValidationError(_('Could not resolve %s' % smtp_host))
                else:
                    try:
                        # Try connecting
                        smtp = LilyIMAP(ssl=data.get('smtp_ssl'), test=True, host=smtp_host, port=int(data.get('smtp_port')), username=self.username, password=self.password)
                        smtp_server = smtp.get_smtp_server(fail_silently=False)
                        smtp_server.open()
                        smtp_server.close()
                    except SMTPAuthenticationError, e:
                        raise forms.ValidationError(_('Unable to login with provided username and password on the SMTP host'))
                    except Exception, e:
                        print traceback.format_exc(e)
                        raise forms.ValidationError(_('Could not connect to %s:%s' % (smtp_host, data.get('smtp_port'))))
            except:
                raise
            finally:
                socket.setdefaulttimeout(defaulttimeout)

        return data


class EmailConfigurationStep3Form(Form, FieldInitFormMixin):
    """
    Fields in e-mail configuration wizard step 3.
    """
    name = forms.CharField(max_length=255, label=_('Your name'), widget=forms.TextInput(attrs={
        'placeholder': _('First Last')
    }))
    signature = forms.CharField(label=_('Your signature'), widget=forms.Textarea(attrs={
        'click_and_show': False,
    }), required=False)

    def __init__(self, *args, **kwargs):
        super(EmailConfigurationStep3Form, self).__init__(*args, **kwargs)
