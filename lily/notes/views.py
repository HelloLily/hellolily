from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.views.generic.edit import DeleteView

from lily.notes.models import Note


class DeleteNoteView(DeleteView):
    """
    Delete an instance and all instances of m2m relationships.
    """
    model = Note
    
    def delete(self, request, *args, **kwargs):
        """
        Overloading super().delete to remove the related models and the instance itself.
        """
        self.object = self.get_object()
        print "test"
        self.object.delete()
        
        # Return response 
        return HttpResponse(simplejson.dumps({
            'html': _('The note was successfully deleted.'),
        }))


delete_note_view = login_required(DeleteNoteView.as_view())