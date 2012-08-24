from crispy_forms.layout import Layout, HTML
from django import forms
from django.forms import ModelForm
from django.forms.widgets import CheckboxInput, PasswordInput, DateInput, TextInput, Select, \
    Textarea, HiddenInput
from django.utils.translation import ugettext as _

from lily.utils.formhelpers import LilyFormHelper
from lily.utils.layout import MultiField, Anchor, ColumnedRow, Column, InlineRow
from lily.utils.models import EmailAddress, PhoneNumber, Address, COUNTRIES
from lily.utils.widgets import JqueryPasswordInput


#===================================================================================================
# Mixins
#===================================================================================================
class FieldInitFormMixin(forms.BaseForm):
    """
    FormMixin to set default widget attributes
    """
    default_widget_attrs = {
        CheckboxInput: {
            'class': {
                'append': True,
                'value': 'tabbable',
            },
        },
        DateInput: {
            'class': {
                'append': True,
                'value': 'mws-textinput tabbable datepicker',
            },
            'placeholder': {
                'value': 'dd/mm/yyyy',
            },
        },
        JqueryPasswordInput: {
            'class': {
                'append': True,
                'value': 'mws-textinput tabbable',
            },
        },                  
        PasswordInput: {
            'class': {
                'append': True,
                'value': 'mws-textinput tabbable',
            },
        },
        Select: {
            'class': {
                'append': True,
                'value': 'chzn-select tabbable',
            },
        },
        TextInput: {
            'class': {
                'append': True,
                'value': 'mws-textinput tabbable',
            },
        },
        Textarea: {
            'class': {
                'append': True,
                'value': 'mws-textinput tabbable',
            },
            'rows': {
                'overwrite_defaults': True,
                'value': '4',
            },
            'cols': {
                'overwrite_defaults': True,
                'value': '55',
            },
        },
    }
    
    def __init__(self, *args, **kwargs):
        super(FieldInitFormMixin, self).__init__(*args, **kwargs)
        for name, field in self.base_fields.items():
            w = field.widget
            if issubclass(w.__class__, HiddenInput):
                continue # ignore
            
            # set placeholder if not already and field has an initial value or label
            if not 'placeholder' in w.attrs:
                if isinstance(w, TextInput) and field.initial is not None:
                    w.attrs['placeholder'] = field.initial
                elif field.label is not None:
                    if w.__class__ in [JqueryPasswordInput, PasswordInput, TextInput, Textarea]:
                        w.attrs['placeholder'] = field.label
            
            if w.__class__ is Textarea:
                # Text for click-show plugin
                if w.attrs.get('click_show_text', False):
                    w.click_show_text = w.attrs['click_show_text']
                else:
                    w.click_show_text = _('Add')
                w.click_and_show = w.attrs.get('click_and_show', True)
                    
            
            # append certain default attributes
            attrs = self.default_widget_attrs.get(w.__class__, [])
            for attr in attrs:
                if attrs[attr].get('append', False):
                    w.attrs[attr] = (w.attrs.get(attr, '') + ' ' + attrs[attr]['value']).strip()
                elif attrs[attr].get('overwrite_defaults', False):
                    w.attrs[attr] = attrs[attr]['value']
                else:
                    w.attrs[attr] = w.attrs.get(attr, attrs[attr]['value'])
            
            # add class for required fields
            if field.required:
                w.attrs['class'] = (w.attrs.get('class', '') + ' required').strip()
                
        super(FieldInitFormMixin, self).__init__(*args, **kwargs)


#===================================================================================================
# Forms
#===================================================================================================
class EmailAddressBaseForm(ModelForm, FieldInitFormMixin):
    """
    Form for adding an e-mail address, only including the is_primary and the e-mail fields.
    """
    def __init__(self, *args, **kwargs):
        super(EmailAddressBaseForm, self).__init__(*args, **kwargs)
        self.helper = LilyFormHelper(self)
        self.helper.form_tag = False
        self.helper.add_layout(Layout(
            MultiField(
                None,
                ColumnedRow(
                    Column('email_address', size=2, first=True),
                    Column(
                        HTML('''
                            <label>
                                <input class="hidden" type="radio" value="{{ form.prefix }}" name="{{ formset.prefix }}_primary-email" {% if form.instance.is_primary %}checked="checked"{% endif %}/>
                                <span class="{% if form.instance.is_primary %}checked {% endif %}tabbable">''' + _('primary') + '''</span>
                            </label>'''
                        ),
                        size=2,
                        css_class='center email_is_primary'),
                    Column(
                        Anchor(href='javascript:void(0)', css_class='i-16 i-trash-1 blue {{ formset.prefix }}-delete-row'),
                        size=1,
                        css_class='formset-delete'
                    ),
                )
            )
        ))
        
        self.fields['email_address'].label = ''
        self.fields['is_primary'].label = ''
        
    class Meta:
        model = EmailAddress
        fields = ('email_address', 'is_primary')
        exclude = ('status')
        widgets = {
            'email_address': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('E-mail address'),
            }),
        }

 
class PhoneNumberBaseForm(ModelForm, FieldInitFormMixin):
    """
    Form for adding a phone number, only including the number and type/other type fields.
    """
    type = forms.ChoiceField(choices=PhoneNumber.PHONE_TYPE_CHOICES, initial='work', required=False,
        widget=forms.Select(attrs={
            'class': 'other chzn-select-no-search tabbable'
        }
    ))

    # Make raw_input not required to prevent the form from demanding input when only type
    # has been changed.
    raw_input = forms.CharField(label=_('Phone number'), required=False);
    
    def __init__(self, *args, **kwargs):
        super(PhoneNumberBaseForm, self).__init__(*args, **kwargs)
        self.helper = LilyFormHelper(self)
        self.helper.form_tag = False
        self.helper.add_layout(Layout(
            MultiField(
                None,
                ColumnedRow(
                    Column('raw_input', size=2, first=True),
                    Column('type', size=2),
                    Column('other_type', size=2),
                    Column(
                        Anchor(href='javascript:void(0)', css_class='i-16 i-trash-1 blue {{ formset.prefix }}-delete-row'),
                        size=1,
                        css_class='formset-delete'
                    ),
                )
            )
        ))
        
        self.fields['raw_input'].label = ''
        self.fields['type'].label = ''
        self.fields['other_type'].label = ''

    class Meta:
        model = PhoneNumber
        fields = ('raw_input', 'type', 'other_type')
        exclude = ('status')
        widgets = {
            'other_type': forms.TextInput(attrs={
                'class': 'other hidden',
            }),
        }


class AddressBaseForm(ModelForm, FieldInitFormMixin):
    """
    Form for adding an address which includes all fields available.
    """
    type = forms.ChoiceField(choices=Address.ADDRESS_TYPE_CHOICES, initial='visiting',
        widget=forms.Select(attrs={
            'class': 'chzn-select-no-search',
        })
    )
    country = forms.ChoiceField(choices=COUNTRIES, required=False)

    def __init__(self, *args, **kwargs):
        super(AddressBaseForm, self).__init__(*args, **kwargs)
        
        if hasattr(self, 'exclude_address_types'):
            choices = self.fields['type'].choices
            for i in reversed(range(len(choices))):
                if choices[i][0] in self.exclude_address_types:
                    del choices[i]
            self.fields['type'].choices = choices
        
        self.helper = LilyFormHelper(self)
        self.helper.form_tag = False
        self.helper.add_layout(Layout(
            MultiField(
                None,
                ColumnedRow(
                    Column(
                        MultiField(
                            None,
                            InlineRow(ColumnedRow(
                                Column('street', size=3, first=True),
                                Column('street_number', size=2),
                                Column('complement', size=2),
                                Column(
                                    Anchor(href='javascript:void(0)', css_class='i-16 i-trash-1 blue {{ formset.prefix }}-delete-row'),
                                    size=1,
                                    css_class='formset-delete'
                                ),
                            )),
                            InlineRow(ColumnedRow(
                                Column('postal_code', size=3, first=True),
                                Column('city', size=4),
                            )),     
                            InlineRow(ColumnedRow(
                                Column('country', size=4, first=True),
                                Column('type', size=3),
                            )),
                        ),
                        size=7,
                        first=True
                    ),
                    Column(
                        HTML('<br /><hr />'), 
                        size=6, 
                        first=True,
                    ),
                ),
            )
        ))
        
        self.fields['street'].label = ''
        self.fields['street_number'].label = ''
        self.fields['complement'].label = ''
        self.fields['postal_code'].label = ''
        self.fields['city'].label = ''
        self.fields['country'].label = ''
        self.fields['type'].label = ''
            
    class Meta:
        model = Address
        fields = ('street', 'street_number', 'complement', 'postal_code', 'city', 'country', 'type')
        exclude = ('state_provice',)