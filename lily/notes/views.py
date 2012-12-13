from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import DeleteView, UpdateView, FormMixin

from lily.notes.forms import EditNoteForm, NoteForm
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


class NoteDetailViewMixin(FormMixin, SingleObjectMixin, TemplateResponseMixin, View):
    """
    DetailView for models including a NoteForm to quickly add notes.
    """
    form_class = NoteForm
    
    def get(self, request, *args, **kwargs):
        """
        Implementing the response for the http method GET.
        """
        self.object = self.get_object()
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
                
        context = self.get_context_data(object=self.object, form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Implementing the response for the http method POST.
        """
        self.object = self.get_object()
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """
        When adding a note, automatically save the related object and author.
        """
        note = form.save(commit=False)
        note.author = self.request.user
        note.subject = self.object
        note.save()

        return super(NoteDetailViewMixin, self).form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(object=self.object, form=form))

    def get_success_url(self):
        if not hasattr(self, 'success_url_reverse_name'):
            return super(NoteDetailViewMixin, self).get_success_url()
        
        return reverse(self.success_url_reverse_name, kwargs={ 'pk': self.object.pk })


delete_note_view = login_required(DeleteNoteView.as_view())
edit_note_view = login_required(EditNoteView.as_view())
