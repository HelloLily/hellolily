from django.forms import ModelForm

from lily.notes.models import Note
from lily.utils.functions import autostrip


class EditNoteForm(ModelForm):
    """
    This form is a subclass from the default AuthenticationForm.
    We just add classes to the fields here, validation is done in the parent form.
    """
    class Meta:
        model = Note
        exclude = ('author', )

EditNoteForm = autostrip(EditNoteForm)