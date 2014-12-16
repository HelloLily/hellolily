import json
from urlparse import urlparse

import anyjson
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _, ungettext
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.notes.models import Note
from lily.utils.functions import is_ajax
from lily.utils.views import AjaxUpdateView, ArchiveView, UnarchiveView, AngularView
from lily.utils.views.mixins import HistoryListViewMixin, LoginRequiredMixin


from .forms import CreateUpdateCaseForm, CreateCaseQuickbuttonForm
from .models import Case, CaseStatus


class ListCaseView(LoginRequiredMixin, AngularView):
    """
    Display a list of all cases.
    """
    template_name = 'cases/case_list.html'


class DetailCaseView(LoginRequiredMixin, HistoryListViewMixin):
    """
    Display a detail page for a single case.
    """
    model = Case

    def get_context_data(self, **kwargs):
        context = super(DetailCaseView, self).get_context_data(**kwargs)
        context.update({
            'status_choices': CaseStatus.objects.all()
        })
        return context


class CreateUpdateCaseMixin(LoginRequiredMixin):
    form_class = CreateUpdateCaseForm
    model = Case

    def get_context_data(self, **kwargs):
        """
        Provide an url to go back to.
        """
        kwargs = super(CreateUpdateCaseMixin, self).get_context_data(**kwargs)
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


class CreateCaseView(CreateUpdateCaseMixin, CreateView):
    def dispatch(self, request, *args, **kwargs):
        """
        For AJAX calls, use a different form and template.
        """
        if is_ajax(request):
            self.template_name_suffix = '_form_ajax'
            self.form_class = CreateCaseQuickbuttonForm

        return super(CreateCaseView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        """
        Set the initials for the form
        """
        initial = super(CreateCaseView, self).get_initial()

        # If the Case is created from an Account, initialize the form with data from that Account
        account_pk = self.kwargs.get('account_pk', None)
        if account_pk:
            try:
                account = Account.objects.get(pk=account_pk)
            except Account.DoesNotExist:
                pass
            else:
                initial.update({'account': account})

        # If the Case is created from a Contact, initialize the form with data from that Contact
        contact_pk = self.kwargs.get('contact_pk', None)
        if contact_pk:
            try:
                contact = Contact.objects.get(pk=contact_pk)
            except Contact.DoesNotExist:
                pass
            else:
                initial.update({'contact': contact})
                # If the Contact only works at one Account, set that as initial account
                if contact.functions.count() == 1:
                    account = contact.functions.first().account
                    initial.update({'account': account})

        # If the Case is created from a Note, initialize the form with data from that Note:
        # Note content -> description, Note subject -> account or contact, depending on the content type.
        note_pk = self.kwargs.get('note_pk', None)
        if note_pk:
            try:
                note = Note.objects.get(pk=note_pk)
            except Note.DoesNotExist:
                pass
            else:
                initial.update({'description': note.content})
                if note.content_type.model == 'account':
                    initial.update({'account': note.subject})
                elif note.content_type.model == 'contact':
                    initial.update({'contact': note.subject})

        return initial

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

            response = anyjson.serialize({
                'error': False,
                'redirect_url': redirect_url
            })
            return HttpResponse(response, content_type='application/json')

        return response

    def form_invalid(self, form):
        response = self.render_to_response(self.get_context_data(form=form))
        if is_ajax(self.request):
            response = anyjson.serialize({
                'error': True,
                'html': response.rendered_content
            })
            return HttpResponse(response, content_type='application/json')

        return response


class UpdateCaseView(CreateUpdateCaseMixin, UpdateView):
    model = Case

    def form_valid(self, form):
        # Saves the instance
        response = super(UpdateCaseView, self).form_valid(form)

        # Show save message
        messages.success(self.request, _('%s (Case) has been updated.') % self.object.subject)

        return response


class ArchiveCasesView(LoginRequiredMixin, ArchiveView):
    """
    Archives one or more cases.
    """
    model = Case
    success_url = reverse_lazy('case_list')

    def archive(self, archive=True, **kwargs):
        """
        Set Case to archived and status to last position (probably closed status)

        Arguments:
            archive (boolean): True if object should be archived, False to unarchive.
        """
        kwargs.update({'status': CaseStatus.objects.last()})

        # Even if the status can't be set we can still archive the case
        return super(ArchiveCasesView, self).archive(**kwargs)

    def get_success_message(self, count):
        message = ungettext(
            _('Case has been archived.'),
            _('%d cases have been archived.') % count,
            count
        )
        messages.success(self.request, message)


class UnarchiveCasesView(LoginRequiredMixin, UnarchiveView):
    """
    Unarchives one or more cases.
    """
    model = Case
    success_url = reverse_lazy('case_archived_list')

    def get_success_message(self, count):
        message = ungettext(
            _('Case has been unarchived.'),
            _('%d cases have been unarchived.') % count,
            count
        )
        messages.success(self.request, message)


class UpdateAndUnarchiveCaseView(CreateUpdateCaseMixin, UpdateView):
    """
    Allows a case to be unarchived and edited if needed
    """
    model = Case

    def dispatch(self, request, *args, **kwargs):
        # Change form and template for ajax calls
        if is_ajax(request):
            self.form_class = CreateUpdateCaseForm
            self.template_name = 'cases/case_unarchive_form.html'

        return super(UpdateAndUnarchiveCaseView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Makes sure the case gets unarchived when the object is saved
        self.object.is_archived = False

        # Saves the instance
        super(UpdateAndUnarchiveCaseView, self).form_valid(form)

        # Show save message
        messages.success(self.request, _('%s (Case) has been unarchived.') % self.object.subject)

        response = anyjson.serialize({
            'error': False,
            'redirect_url': self.get_success_url()
        })
        return HttpResponse(response, content_type='application/json')

    def get_success_url(self):
        return reverse('case_details', kwargs={
            'pk': self.object.id
        })


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
            response = anyjson.serialize({
                'error': False,
                'redirect_url': redirect_url
            })
            return HttpResponse(response, content_type='application/json')

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
            case = Case.objects.get(pk=kwargs.pop('pk'))
        except Case.DoesNotExist:
            messages.error(self.request, _('Status could not be changed'))
            raise Http404()

        if 'status' not in request.POST.keys() or len(request.POST.keys()) != 1:
            messages.error(self.request, _('Status could not be changed'))
            raise Http404()

        try:
            status = CaseStatus.objects.get(pk=int(request.POST['status']))
        except ValueError, CaseStatus.DoesNotExist:
            messages.error(self.request, _('Status could not be changed'))
            raise Http404()

        case.status = status
        case.save()

        message = _('Status has been changed to %s') % status
        messages.success(self.request, message)
        # Return response
        return HttpResponse(json.dumps({'status': status.status}), content_type='application/json')
