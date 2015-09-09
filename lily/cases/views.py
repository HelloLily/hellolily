import json
from urlparse import urlparse

import anyjson
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.notes.models import Note
from lily.tenant.middleware import get_current_user
from lily.users.models import LilyUser
from lily.utils.functions import is_ajax
from lily.utils.views import AjaxUpdateView
from lily.utils.views.mixins import LoginRequiredMixin


from .forms import CreateUpdateCaseForm, CreateCaseQuickbuttonForm
from .models import Case, CaseStatus, CaseType


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

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        if self.object:
            return '/#/cases/' + str(self.object.id)
        else:
            return '/#cases'


class UpdateCaseView(CreateUpdateCaseMixin, UpdateView):
    model = Case

    def form_valid(self, form):
        # Saves the instance
        response = super(UpdateCaseView, self).form_valid(form)

        # Show save message
        messages.success(self.request, _('%s (Case) has been updated.') % self.object.subject)

        return response

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        # return '/#/cases/%s' % self.object.pk
        return '/#/cases'


class ArchiveCasesView(LoginRequiredMixin, AjaxUpdateView):
    """
    Archives a case.
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        """
        Set case to archived and status to last position (probably closed status)

        Arguments:
            archive (boolean): True if object should be archived, False to unarchive.
        """
        try:
            if 'id' in request.POST.keys():
                new_status = CaseStatus.objects.last()

                instance = Case.objects.get(pk=int(request.POST['id']))

                instance.is_archived = True
                instance.status = new_status

                instance.save()
            else:
                messages.error(self.request, _('Case could not be archived'))
                raise Http404()
        except:
            messages.error(self.request, _('Case could not be archived'))
            raise Http404()
        else:
            message = _('Case has been archived')
            messages.success(self.request, message)

            return HttpResponse(anyjson.serialize({'status': new_status.status, 'archived': 'true'}), content_type='application/json')


class UnarchiveCasesView(LoginRequiredMixin, AjaxUpdateView):
    """
    Unarchives a case.
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            if 'id' in request.POST.keys():

                instance = Case.objects.get(pk=int(request.POST['id']))

                instance.is_archived = False

                instance.save()
            else:
                messages.error(self.request, _('Case could not be unarchived'))
                raise Http404()
        except:
            messages.error(self.request, _('Case could not be unarchived'))
            raise Http404()
        else:
            message = _('Case has been unarchived')
            messages.success(self.request, message)

            return HttpResponse(anyjson.serialize({'archived': 'false'}), content_type='application/json')


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

        response = anyjson.serialize({
            'error': False,
        })
        return HttpResponse(response, content_type='application/json')


class UpdateStatusAjaxView(AjaxUpdateView):
    """
    View that updates the status field of a Case.
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


class UpdateAssignedToView(AjaxUpdateView):
    """
    View that updates the assigned to field of a Case.
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        """
        Overloading post to update the assigned_to attribute for a Case object.
        """
        assignee = None

        try:
            assignee_id = request.POST.get('assignee', None)

            if assignee_id:
                # FIXME: WORKAROUND FOR TENANT FILTER.
                # An error will occur when using LilyUser.objects.all(), most likely because
                # the foreign key to contact (and maybe account) is filtered and executed before
                # the filter for the LilyUser. This way it's possible contacts (and maybe accounts)
                # won't be found for a user. But since it's a required field, an exception is raised.
                assignee = LilyUser.objects.get(pk=int(assignee_id), tenant=get_current_user().tenant.id)
        except LilyUser.DoesNotExist:
            messages.error(self.request, _('Assignee could not be changed'))
            raise Http404()

        try:
            case = Case.objects.get(pk=kwargs.pop('pk'))
        except Case.DoesNotExist:
            messages.error(self.request, _('Assignee could not be changed'))
            raise Http404()

        case.assigned_to = assignee
        case.save()

        if assignee:
            message = _('Assignee has been changed to %s') % assignee.full_name
            messages.success(self.request, message)
            # Return response
            return HttpResponse(anyjson.serialize({
                'assignee': {
                    'id': assignee.id,
                    'name': assignee.full_name,
                }
            }), content_type='application/json')
        else:
            message = _('Case has been unassigned')
            messages.success(self.request, message)
            # Return response
            return HttpResponse(anyjson.serialize({
                'assignee': None
            }), content_type='application/json')


class GetCaseTypesView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        casetypes_objects = CaseType.objects.filter(is_archived=False, use_as_filter=True)
        casetypes = {}

        for casetypes_object in casetypes_objects:
            casetypes.update({
                casetypes_object.id: casetypes_object.type
            })

        return HttpResponse(anyjson.serialize({
            'casetypes': casetypes,
        }), content_type='application/json')

