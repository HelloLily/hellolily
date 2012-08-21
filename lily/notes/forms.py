from crispy_forms.layout import Submit, Reset
from django import forms
from django.utils.translation import ugettext as _

from lily.notes.models import Note
from lily.utils.formhelpers import LilyFormHelper
from lily.utils.forms import FieldInitFormMixin
from lily.utils.layout import Row, InlineRow, MultiField


class NoteForm(forms.ModelForm, FieldInitFormMixin):
    def __init__(self, *args, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)
        self.helper = LilyFormHelper(self)
        self.helper.replace('note',
           MultiField(
                '',
                'note',
                Submit('submit', _('Add note'), css_id='add-note-button', css_class='small')
           )
        )
        
        self.fields['note'].label = ''
        
    class Meta:
        model = Note
        fields = ('note',)
        exclude = ('is_deleted', 'author', 'object_id', 'content_type')
        widgets = {
            'note': forms.Textarea(attrs={
                'placeholder': _('Write your note here'),
                'click_show': False,
                'field_classes': 'inline note-textarea',
            })
        }


class EditNoteForm(forms.ModelForm, FieldInitFormMixin):
    def __init__(self, *args, **kwargs):
        super(EditNoteForm, self).__init__(*args, **kwargs)
        self.helper = LilyFormHelper(self)
        self.helper.replace('note',
            Row(
                MultiField(
                    self.fields['note'].label,
                    InlineRow('note'),
               ),
            ) 
        )
        
        self.fields['note'].label = ''
        
        self.helper.add_input(Submit('submit', _('Save'), css_class='red'))
        self.helper.add_input(Reset('reset', _('Reset'), css_class='gray'))
    
    class Meta:
        model = Note
        fields = ('note',)
        exclude = ('is_deleted', 'author', 'object_id', 'content_type')
        widgets = {
            'note': forms.Textarea(attrs={
                'class': 'inline note-textarea',
            })
        }
