from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.views.generic.edit import DeleteView, UpdateView

from lily.notes.forms import EditNoteForm
from lily.notes.models import Note
from lily.utils.functions import is_ajax


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
        self.object.delete()
        
        # Return response 
        return HttpResponse(simplejson.dumps({
            'html': _('The note was successfully deleted.'),
        }), mimetype='application/json')
        

class EditNoteView(UpdateView):
    model = Note
    form_class = EditNoteForm
    template_name = 'notes/edit_form.html'
    ajax_template_name = 'notes/list_item.html'
    
    def get_success_url(self):
        return reverse('dashboard')
    
    def form_valid(self, form):
        self.object = form.save()
        
        if is_ajax(self.request):
            context = RequestContext(self.request, self.get_context_data(form=form))
            return HttpResponse(simplejson.dumps({
                'error': False,
                'html': render_to_string(self.ajax_template_name, context_instance=context),
            }), mimetype='application/json')
        
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form):
        if is_ajax(self.request):
            context = RequestContext(self.request, self.get_context_data(form=form))
            return HttpResponse(simplejson.dumps({
                'error': True,
                'html': render_to_string(self.ajax_template_name, context_instance=context)
            }), mimetype='application/json')
        
        return super(EditNoteView, self).form_invalid(form)

delete_note_view = login_required(DeleteNoteView.as_view())
edit_note_view = login_required(EditNoteView.as_view())
