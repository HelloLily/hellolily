import anyjson
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import DeleteView

from lily.tenant.middleware import get_current_user
from lily.users.models import LilyUser
from lily.utils.views import AjaxUpdateView
from lily.utils.views.mixins import LoginRequiredMixin

from .models import Case, CaseStatus


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
        return HttpResponse(anyjson.serialize({'status': status.name}), content_type='application/json')


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
