from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import ugettext as _

from lily.updates.models import BlogEntry
from lily.utils.formhelpers import LilyFormHelper
from lily.utils.forms import FieldInitFormMixin
from lily.utils.layout import MultiField


class CreateBlogEntryForm(forms.ModelForm, FieldInitFormMixin):
    def __init__(self, *args, **kwargs):
        super(CreateBlogEntryForm, self).__init__(*args, **kwargs)
        self.helper = LilyFormHelper(self)
        self.helper.set_form_action('dashboard')
        self.helper.replace('content',
           MultiField(
                None,
                'content',
                Submit('blogentry-submit', _('Post'), css_class='small add-blogentry-button')
           )
        )
    
    class Meta:
        model = BlogEntry
        fields = ('reply_to', 'content',)
        exclude = ('author', 'created', 'deleted',)
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': _('Write something here'),
                'click_show': False,
                'field_classes': 'blogentry-textarea inline',
                'maxlength': 255,
            }),
            'reply_to': forms.HiddenInput(),
        }