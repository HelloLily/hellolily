from urlparse import urlparse

from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.utils.translation import ugettext as _, ungettext
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from lily.cases.forms import CreateUpdateCaseForm, CreateCaseQuickbuttonForm
from lily.cases.models import Case
from lily.notes.models import Note
from lily.utils.functions import is_ajax
from lily.utils.views import SortedListMixin, HistoryListViewMixin, AjaxUpdateView, LoginRequiredMixin, \
    ArchivedFilterMixin, ArchiveView, UnarchiveView


class ListCaseView(LoginRequiredMixin, ArchivedFilterMixin, SortedListMixin, ListView):
    """
    Display a list of all cases.
    """
    model = Case
    sortable = [2, 3, 4, 5, 6]
    default_order_by = 2
    default_sort_order = SortedListMixin.DESC
    template_name = 'cases/case_list_active.html'


class DetailCaseView(LoginRequiredMixin, HistoryListViewMixin):
    """
    Display a detail page for a single case.
    """
    model = Case


class CreateUpdateCaseView(object):
    form_class = CreateUpdateCaseForm
    model = Case

    def get_context_data(self, **kwargs):
        """
        Provide an url to go back to.
        """
        kwargs = super(CreateUpdateCaseView, self).get_context_data(**kwargs)
        if not is_ajax(self.request):
            kwargs.update({
                'back_url': self.get_success_url(),
            })

        return kwargs

    def get_success_url(self):
        """
        Redirect to case list after creating or updating a case.
        """
        return '%s?order_by=7&sort_order=desc' % (reverse('case_list'))


class CreateCaseView(LoginRequiredMixin, CreateUpdateCaseView, CreateView):
    def dispatch(self, request, *args, **kwargs):
        """
        For AJAX calls, use a different form and template.
        """
        if is_ajax(request):
            self.template_name_suffix = '_form_ajax'
            self.form_class = CreateCaseQuickbuttonForm

        return super(CreateCaseView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        '''
        If the Case is created from a Note, initialize the form with data from that Note:
        Note content -> description, Note subject -> account or contact, depending on the content type.
        '''
        kwargs = super(CreateCaseView, self).get_form_kwargs()
        note_pk = self.kwargs.get('note_pk', None)
        print kwargs
        if note_pk:
            note = Note.objects.get(pk=note_pk)
            # If note.subject is None, then the Note's subject is linked to another tenant, e.g. when the note_pk is
            # entered manually in the url. In that case, do nothing. Otherwise, pre-fill the description and account
            # or contact field.
            if note.subject is not None:
                kwargs['initial'].update({'description': note.content})
                if note.content_type.model == 'account':
                    kwargs['initial'].update({'account': note.subject})
                elif note.content_type.model == 'contact':
                    kwargs['initial'].update({'contact': note.subject})

        return kwargs

    def form_valid(self, form):
        # Saves the instance
        response = super(CreateCaseView, self).form_valid(form)

        # Show save message
        message = _('%s (Case) has been created.') % self.object.subject
        messages.success(self.request, message)

        if is_ajax(self.request):
            # Reload when user is in the case list
            redirect_url = None
            parse_result = urlparse(self.request.META['HTTP_REFERER'])
            if parse_result.path == reverse('case_list'):
                redirect_url = '%s?order_by=7&sort_order=desc' % reverse('case_list')

            response = simplejson.dumps({
                'error': False,
                'redirect_url': redirect_url
            })
            return HttpResponse(response, mimetype='application/json')

        return response

    def form_invalid(self, form):
        response = self.render_to_response(self.get_context_data(form=form))
        if is_ajax(self.request):
            response = simplejson.dumps({
                'error': True,
                'html': response.rendered_content
            })
            return HttpResponse(response, mimetype='application/json')

        return response       


class UpdateCaseView(LoginRequiredMixin, CreateUpdateCaseView, UpdateView):
    model = Case

    def form_valid(self, form):
        # Saves the instance
        response = super(UpdateCaseView, self).form_valid(form)

        # Show save message
        messages.success(self.request, _('%s (Case) has been updated.') % self.object.subject)

        return response


class ArchivedCasesView(ListCaseView):
    show_archived = True
    template_name = 'cases/case_list_archived.html'


class ArchiveCasesView(LoginRequiredMixin, ArchiveView):
    """
    Archives one or more cases
    """
    model = Case
    success_url = reverse_lazy('case_list')

    def get_success_message(self, count):
        message = ungettext(
            _('Case has been archived.'),
            _('%d cases have been archived.') % count,
            count
        )
        messages.success(self.request, message)


class UnarchiveCasesView(LoginRequiredMixin, UnarchiveView):
    """
    Archives one or more cases
    """
    model = Case
    success_url = reverse_lazy('case_archived_list')

    def get_success_message(self, count):
        message = ungettext(
            _('Case has been re-activated.'),
            _('%d cases have been re-activated.') % count,
            count
        )
        messages.success(self.request, message)


class DeleteCaseView(LoginRequiredMixin, DeleteView):
    """
    Delete an instance and all instances of m2m relationships.
    """
    model = Case

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        # Show delete message
        messages.success(self.request, _('%s (Case) has been deleted.') % self.object.subject)

        redirect_url = self.get_success_url()
        if is_ajax(request):
            response = simplejson.dumps({
                'error': False,
                'redirect_url': redirect_url
            })
            return HttpResponse(response, mimetype='application/json')

        return HttpResponseRedirect(redirect_url)

    def get_success_url(self):
        return reverse('case_list')


class UpdateStatusAjaxView(AjaxUpdateView):
    """
    View that updates the status-field of a Case.
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        """
        Overloading post to update the status attribute for a Case object.
        """
        try:
            object_id = kwargs.pop('pk')
            instance = Case.objects.get(pk=object_id)

            if 'status' in request.POST.keys() and len(request.POST.keys()) == 1:
                instance.status = int(request.POST['status'])
                instance.save()
            else:
                messages.error(self.request, _('Status could not be changed'))
                raise Http404()
        except:
            messages.error(self.request, _('Status could not be changed'))
            raise Http404()
        else:
            status = Case.STATUS_CHOICES[instance.status][1]
            message = _('Status has been changed to') + ' ' + status
            messages.success(self.request, message)
            # Return response
            return HttpResponse(simplejson.dumps({'status': status}), mimetype='application/json')
