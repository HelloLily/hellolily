from crispy_forms.layout import Submit, Reset
from django import forms
from django.utils.translation import ugettext as _

from lily.notes.models import Note
from lily.utils.formhelpers import LilyFormHelper
from lily.utils.forms import FieldInitFormMixin
from lily.utils.layout import MultiField


class NoteForm(forms.ModelForm, FieldInitFormMixin):
    def __init__(self, *args, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Note
        fields = ('content',)
        exclude = ('is_deleted', 'author', 'object_id', 'content_type')
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': _('Write your note here'),
                'click_show': False,
                'field_classes': 'inline note-textarea',
            })
        }


class UpdateNoteForm(forms.ModelForm, FieldInitFormMixin):
    def __init__(self, *args, **kwargs):
        super(UpdateNoteForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Note
        fields = ('content',)
        exclude = ('is_deleted', 'author', 'object_id', 'content_type')
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'inline note-textarea',
            })
        }
