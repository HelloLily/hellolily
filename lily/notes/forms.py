from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from lily.utils.forms import HelloLilyModelForm
from lily.utils.forms.widgets import LilyDateTimePicker

from .models import Note


class NoteForm(HelloLilyModelForm):
    def __init__(self, *args, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Note
        fields = ('type', 'content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': _('Write your note here'),
                'click_show': False,
                'field_classes': 'inline note-textarea',
                'rows': 1,
            })
        }


class UpdateNoteForm(HelloLilyModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateNoteForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Note
        fields = ('type', 'content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'inline note-textarea',
            })
        }


class UpdateDateNoteForm(HelloLilyModelForm):
    sort_by_date = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS, widget=LilyDateTimePicker(
        options={
            'autoclose': 'false',
        },
        format=settings.DATETIME_INPUT_FORMATS[0],
        attrs={
            'placeholder': LilyDateTimePicker.conv_datetime_format_py2js(settings.DATETIME_INPUT_FORMATS[0]),
        },
    ))

    def __init__(self, *args, **kwargs):
        super(UpdateDateNoteForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Note
        fields = ('sort_by_date',)
        exclude = ('content', 'is_deleted', 'author', 'object_id', 'content_type')
