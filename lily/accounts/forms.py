from django import forms
from django.db.models.query_utils import Q
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _
from lily.accounts.fields import MultipleInputAndChoiceField
from lily.accounts.models import AccountModel, TagModel
from lily.accounts.widgets import InputAndSelectMultiple
from lily.utils.functions import autostrip
from lily.utils.models import EmailAddressModel


class AddAccountMinimalForm(forms.models.ModelForm):
    """
    Form to add an account with the absolute minimum of information.
    """
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={
        'class': 'mws-textinput required',
        'placeholder': _('Company name')
    }))
    
    email = forms.EmailField(label=_('E-mail'), max_length=255, widget=forms.TextInput(attrs={
        'class': 'mws-textinput required',
        'placeholder': _('E-mail address')
    }))
    
    website = forms.URLField(max_length=30, initial='http://', required=False,
        widget=forms.TextInput(attrs={
            'class': 'mws-textinput',
    }))
    
    def clean(self):
        """
        Form validation: all fields should be unique.
        """
        cleaned_data = super(AddAccountMinimalForm, self).clean()
        
        if cleaned_data.get('name'):
            try:
                AccountModel.objects.get(name=cleaned_data.get('name'))
                self._errors['name'] = self.error_class([_('Name already in use.')])
            except AccountModel.DoesNotExist:
                pass
            
        if cleaned_data.get('email'): 
            try:
                EmailAddressModel.objects.get(email_address=cleaned_data.get('email'))            
                self._errors['email'] = self.error_class([_('E-mail address already in use.')])
            except EmailAddressModel.DoesNotExist:
                pass
            except EmailAddressModel.MultipleObjectsReturned: 
                self._errors['email'] = self.error_class([_('E-mail address already in use.')])
        
        if cleaned_data.get('website'):
            try:
                AccountModel.objects.get(website=cleaned_data.get('website'))
                self._errors['website'] = self.error_class([_('Website already in use.')])
            except AccountModel.DoesNotExist:
                pass
        
        return cleaned_data
        
    class Meta:
        model = AccountModel
        fields = ('name', 'email', 'website')

AddAccountMinimalForm = autostrip(AddAccountMinimalForm)


class AddAccountForm(forms.models.ModelForm):
    """
    Form for adding an account which includes all fields available.
    
    TODO: status field
    """
    twitter = forms.CharField(label=_('Twitter'), required=False, max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'mws-textinput',
            'placeholder': _('Twitter username')
    }))
    
    linkedin = forms.CharField(label=_('LinkedIn'), required=False, max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'mws-textinput',
            'placeholder': _('LinkedIn username')
    }))
    
    facebook = forms.URLField(label=_('Facebook'), required=False,
        widget=forms.TextInput(attrs={
            'class': 'mws-textinput',
            'placeholder': _('Facebook profile link')
    }))
    
    tags = MultipleInputAndChoiceField(queryset=TagModel.objects.all(), required=False,
        widget=InputAndSelectMultiple(attrs={
            'class': 'input-and-choice-select',
    }))

    def __init__(self, user=None, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):
        
        super(AddAccountForm, self).__init__(data, files, auto_id, prefix,
                 initial, error_class, label_suffix,
                 empty_permitted, instance)
    
        # TODO: Limit queryset to tags used by accounts created by users from user's account or
        # tags used by accounts linked to the user's client
#        self.fields['tags'].queryset = user.account.tags.all()
    
    def save(self, commit=True):
        """
        Overloading super().save to create save tags and create the relationships with
        this account instance. Needs to be done here because the TagModels are expected to exist
        before self.instance is saved.
        """
        instance = super(AddAccountForm, self).save(commit=False)
        
        if commit:
            instance.save()
            
        tags = self.cleaned_data['tags']
        for tag in tags:
            # Create relationship with TagModel
            tag_instance, created = TagModel.objects.get_or_create(tag=tag)
            instance.tags.add(tag_instance)
        
        return instance
    
    class Meta:
        model = AccountModel
        fields = ('name', 'tags', 'twitter', 'facebook', 'linkedin', 'website', 'description')
                
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mws-textinput required',
                'placeholder': _('Company name'),
            }),
            'website': forms.TextInput(attrs={
                'class': 'mws-textinput required',
            }),
        }

AddAccountForm = autostrip(AddAccountForm)


class EditAccountForm(forms.models.ModelForm):
    """
    Form for editing an existing account which includes all fields available.
    
    TODO: status field
    """
    website = forms.URLField(max_length=30, initial='http://', required=False,
        widget=forms.TextInput(attrs={
            'class': 'mws-textinput',
    }))
    
    twitter = forms.CharField(label=_('Twitter'), required=False, max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'mws-textinput',
            'placeholder': _('Twitter username')
    }))
    
    linkedin = forms.CharField(label=_('LinkedIn'), required=False, max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'mws-textinput',
            'placeholder': _('LinkedIn username')
    }))
    
    facebook = forms.URLField(label=_('Facebook'), required=False,
        widget=forms.TextInput(attrs={
            'class': 'mws-textinput',
            'placeholder': _('Facebook profile link')
    }))
    
    tags = MultipleInputAndChoiceField(queryset=TagModel.objects.all(), required=False,
        widget=InputAndSelectMultiple(attrs={
            'class': 'input-and-choice-select',
    }))

    def __init__(self, user=None, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):
        
        super(EditAccountForm, self).__init__(data, files, auto_id, prefix,
                 initial, error_class, label_suffix,
                 empty_permitted, instance)
        
        # TODO: Limit queryset to tags used by accounts created by users from user's account or
        # tags used by accounts linked to the user's client
#        self.fields['tags'].queryset = user.account.tags.all()
    
    def save(self, commit=True):
        """
        Overloading super().save to create save tags and create the relationships with
        this account instance. Needs to be done here because the TagModels are expected to exist
        before self.instance is saved.
        """
        instance = super(EditAccountForm, self).save(commit=False)
        
        if commit:
            instance.save()
        
        tags = self.cleaned_data.get('tags')
        for tag in tags:
            # Create relationship with TagModel
            tag_instance, created = TagModel.objects.get_or_create(tag=tag)
            instance.tags.add(tag_instance)
        
        # Remove any relationships for these tag models with instance
        models = instance.tags.filter(~Q(tag__in=tags))
        for model in models:
            instance.tags.remove(model)
        
        return instance
    
    class Meta:
        model = AccountModel
        fields = ('name', 'tags', 'twitter', 'facebook', 'linkedin', 'website', 'description')
                
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mws-textinput required',
                'placeholder': _('Company name'),
            })
        }

EditAccountForm = autostrip(EditAccountForm)
