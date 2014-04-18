from urlparse import urlparse
import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.utils.datastructures import SortedDict
from django.utils.timezone import utc
from django.utils.translation import ugettext as _
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from pytz import timezone

from lily.deals.forms import CreateUpdateDealForm, CreateDealQuickbuttonForm
from lily.deals.models import Deal
from lily.utils.functions import is_ajax
from lily.utils.views import SortedListMixin, AjaxUpdateView, DeleteBackAddSaveFormViewMixin, HistoryListViewMixin, \
    DeleteBackAddSaveFormViewMixin, HistoryListViewMixin, ArchivedFilterMixin, ArchiveView, UnarchiveView, \
    LoginRequiredMixin


class ListDealView(LoginRequiredMixin, ArchivedFilterMixin, SortedListMixin, ListView):
    """
    Display a list of all deals.
    """
    model = Deal
    sortable = [1, 2, 3, 4, 5, 6, 7]
    default_order_by = 1
    template_name = 'deals/deal_list_active.html'


class ArchivedDealsView(ListDealView):
    show_archived = True
    template_name = 'deals/deal_list_archived.html'


class ArchiveDealsView(LoginRequiredMixin, ArchiveView):
    """
    Archives one or more cases
    """
    model = Deal
    success_url = 'deal_list'

    def get_success_message(self):
        n = len(self.get_object_pks())
        if n == 1:
            message = _('Deal has been archived.')
        else:
            message = _('%d deals have been archived.') % n
        messages.success(self.request, message)


class UnarchiveDealsView(LoginRequiredMixin, UnarchiveView):
    """
    Archives one or more cases
    """
    model = Deal
    success_url = 'deal_archived_list'

    def get_success_message(self):
        n = len(self.get_object_pks())
        if n == 1:
            message = _('Deal has been re-activated.')
        else:
            message = _('%d deals have been re-activated.') % n
        messages.success(self.request, message)


class DetailDealView(LoginRequiredMixin, HistoryListViewMixin):
    """
    Display a detail page for a single deal.
    """
    model = Deal


class CreateUpdateDealView(LoginRequiredMixin, DeleteBackAddSaveFormViewMixin):
    """
    Base class for CreateDealView and UpdateDealView.
    """
    form_class = CreateUpdateDealForm
    model = Deal

    def get_context_data(self, **kwargs):
        """
        Provide an url to go back to.
        """
        kwargs = super(CreateUpdateDealView, self).get_context_data(**kwargs)
        if not is_ajax(self.request):
            kwargs.update({
                'back_url': self.get_success_url(),
            })

        return kwargs

    def form_valid(self, form):
        """
        Overloading super().form_valid to add success message after editing.
        """
        # Save instance
        response = super(CreateUpdateDealView, self).form_valid(form)

        # Set closed_date after changing stage to lost/won and reset it when it's new/pending
        if self.object.stage in [1, 3]:
            self.object.closed_date = datetime.datetime.utcnow().replace(tzinfo=utc)
        elif self.object.stage in [0, 2]:
            self.object.closed_date = None
        self.object.save()

        return response

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        return '%s?order_by=7&sort_order=desc' % (reverse('deal_list'))


class CreateDealView(CreateUpdateDealView, CreateView):
    def dispatch(self, request, *args, **kwargs):
        """
        For AJAX calls, use a different form and template.
        """
        if is_ajax(request):
            self.template_name_suffix = '_form_ajax'
            self.form_class = CreateDealQuickbuttonForm

        return super(CreateDealView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Saves the instance
        response = super(CreateDealView, self).form_valid(form)

        # Show save message
        message = _('%s (Deal) has been created.') % self.object.name
        messages.success(self.request, message)

        if is_ajax(self.request):
            # Reload when user is in the deal list
            redirect_url = None
            parse_result = urlparse(self.request.META['HTTP_REFERER'])
            if parse_result.path == reverse('deal_list'):
                redirect_url = '%s?order_by=7&sort_order=desc' % reverse('deal_list')

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


class UpdateDealView(CreateUpdateDealView, UpdateView):
    model = Deal

    def form_valid(self, form):
        # Saves the instance
        response = super(UpdateDealView, self).form_valid(form)

        # Show save message
        messages.success(self.request, _('%s (Deal) has been updated.') % self.object.name)

        return response


class DeleteDealView(LoginRequiredMixin, DeleteView):
    """
    Delete an instance and all instances of m2m relationships.
    """
    model = Deal

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        # Show delete message
        messages.success(self.request, _('%s (Deal) has been deleted.') % self.object.name)

        redirect_url = self.get_success_url()
        if is_ajax(request):
            response = simplejson.dumps({
                'error': False,
                'redirect_url': redirect_url
            })
            return HttpResponse(response, mimetype='application/json')

        return HttpResponseRedirect(redirect_url)

    def get_success_url(self):
        return reverse('deal_list')


class UpdateStageAjaxView(LoginRequiredMixin, AjaxUpdateView):
    """
    View that updates the stage-field of a Deal.
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        """
        Overloading post to update the stage and closed_date attributes for a Deal object.
        """
        try:
            object_id = kwargs.pop('pk')
            instance = Deal.objects.get(pk=object_id)

            if 'stage' in request.POST.keys() and len(request.POST.keys()) == 1:
                instance.stage = int(request.POST['stage'])

                if instance.stage in [1, 3]:
                    instance.closed_date = datetime.datetime.utcnow().replace(tzinfo=utc)
                elif instance.stage in [0, 2]:
                    instance.closed_date = None

                instance.save()
            else:
                messages.error(self.request, _('Stage could not be changed'))
                raise Http404()
        except:
            messages.error(self.request, _('Stage could not be changed'))
            raise Http404()
        else:
            message = _('Stage has been changed to') + ' ' + Deal.STAGE_CHOICES[instance.stage][1]
            messages.success(self.request, message)
            # Return response
            if instance.closed_date is None:
                return HttpResponse(simplejson.dumps({}), mimetype='application/json')
            else:
                closed_date_local = instance.closed_date.astimezone(timezone(settings.TIME_ZONE))
                return HttpResponse(simplejson.dumps({'closed_date': closed_date_local.strftime('%d %b %y %H:%M')}), mimetype='application/json')
