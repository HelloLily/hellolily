import datetime
from urlparse import urlparse

import anyjson
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils.datastructures import SortedDict
from django.utils.timezone import utc
from django.utils.translation import ugettext as _, ungettext
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from pytz import timezone

from lily.deals.forms import CreateUpdateDealForm, CreateDealQuickbuttonForm
from lily.deals.models import Deal
from lily.utils.functions import is_ajax
from lily.utils.views import AjaxUpdateView, DataTablesListView, ArchiveView, UnarchiveView
from lily.utils.views.mixins import SortedListMixin, DeleteBackAddSaveFormViewMixin, HistoryListViewMixin, \
    ArchivedFilterMixin, LoginRequiredMixin



class ListDealView(LoginRequiredMixin, ArchivedFilterMixin, SortedListMixin, DataTablesListView):
    """
    Display a list of all deals.
    """
    model = Deal
    template_name = 'deals/deal_list_active.html'

    # SortedListMxin
    sortable = [2, 3, 4, 5, 6, 7, 8]
    default_order_by = 2

    # DataTablesListView
    columns = SortedDict([
        ('checkbox', {
            'mData': 'checkbox',
            'bSortable': False,
        }),
        ('edit', {
            'mData': 'edit',
            'bSortable': False,
        }),
        ('name', {
            'mData': 'name',
        }),
        ('account', {
            'mData': 'account',
        }),
        ('stage', {
            'mData': 'stage',
        }),
        ('amount', {
            'mData': 'amount',
        }),
        ('assigned_to', {
            'mData': 'assigned_to',
        }),
        ('closed_date', {
            'mData': 'closed_date',
            'sClass': 'visible-md visible-lg',
        }),
        ('created', {
            'mData': 'created',
            'sClass': 'visible-md visible-lg',
        }),
    ])

    # DataTablesListView
    search_fields = [
        'name__icontains',
        'account__name__icontains',
        'assigned_to__contact__last_name__icontains',
        'assigned_to__contact__first_name__icontains',
    ]

    def order_queryset(self, queryset, column, sort_order):
        """
        Orders the queryset based on given column and sort_order.

        Used by DataTablesListView.
        """
        prefix = ''
        if sort_order == 'desc':
            prefix = '-'
        if column in ('stage', 'amount', 'created'):
            return queryset.order_by('%s%s' % (prefix, column))
        elif column == 'name':
            return queryset.order_by('%saccount' % prefix)
        elif column == 'closed_date':
            return queryset.order_by(
                '%sexpected_closing_date' % prefix,
                '%sclosed_date' % prefix,
            )
        elif column == 'account':
            return queryset.order_by(
                '%saccount__name' % prefix,
            )
        elif 'assigned_to':
            return queryset.order_by(
                '%sassigned_to__contact__last_name' % prefix,
                '%sassigned_to__contact__first_name' % prefix,
            )
        return queryset


class ArchivedDealsView(ListDealView):
    show_archived = True
    template_name = 'deals/deal_list_archived.html'


class ArchiveDealsView(LoginRequiredMixin, ArchiveView):
    """
    Archives one or more deals.
    """
    model = Deal
    success_url = reverse_lazy('deal_list')

    def get_success_message(self, count):
        message = ungettext(
            _('Deal has been archived.'),
            _('%d deals have been archived.') % count,
            count
        )
        messages.success(self.request, message)


class UnarchiveDealsView(LoginRequiredMixin, UnarchiveView):
    """
    Unarchives one or more deals.
    """
    model = Deal
    success_url = reverse_lazy('deal_archived_list')

    def get_success_message(self, count):
        message = ungettext(
            _('Deal has been unarchived.'),
            _('%d deals have been unarchived.') % count,
            count
        )
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
        return '%s?order_by=8&sort_order=desc' % (reverse('deal_list'))


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
                redirect_url = '%s?order_by=8&sort_order=desc' % reverse('deal_list')

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


class UpdateDealView(CreateUpdateDealView, UpdateView):
    model = Deal

    def form_valid(self, form):
        # Saves the instance
        response = super(UpdateDealView, self).form_valid(form)

        # Show save message
        messages.success(self.request, _('%s (Deal) has been updated.') % self.object.name)

        return response


class UpdateAndUnarchiveDealView(CreateUpdateDealView, UpdateView):
    """
    Allows a deal to be unarchived and edited if needed
    """
    model = Deal

    def dispatch(self, request, *args, **kwargs):
        # Change form and template for ajax calls
        if is_ajax(request):
            self.form_class = CreateUpdateDealForm
            self.template_name = 'deals/deal_unarchive_form.html'

        return super(UpdateAndUnarchiveDealView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Makes sure the deal gets unarchived when the object is saved
        self.object.is_archived = False

        # Saves the instance
        super(UpdateAndUnarchiveDealView, self).form_valid(form)

        # Show save message
        messages.success(self.request, _('%s (Deal) has been unarchived.') % self.object.name)

        response = anyjson.serialize({
            'error': False,
            'redirect_url': self.get_success_url()
        })
        return HttpResponse(response, content_type='application/json')

    def get_success_url(self):
        return reverse('deal_details', kwargs={
            'pk': self.object.id
        })


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
            response = anyjson.serialize({
                'error': False,
                'redirect_url': redirect_url
            })
            return HttpResponse(response, content_type='application/json')

        return HttpResponseRedirect(redirect_url)

    def get_success_url(self):
        return reverse('deal_list')


class UpdateStageAjaxView(AjaxUpdateView):
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
            stage = Deal.STAGE_CHOICES[instance.stage][1]
            # Return response
            if instance.closed_date is None:
                return HttpResponse(anyjson.serialize({'stage': stage}), content_type='application/json')
            else:
                closed_date_local = instance.closed_date.astimezone(timezone(settings.TIME_ZONE))
                response = anyjson.serialize({'closed_date': closed_date_local.strftime('%d %b %y %H:%M'), 'stage': stage})
                return HttpResponse(response, mimetype='application/json')
