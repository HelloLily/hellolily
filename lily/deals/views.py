from urlparse import urlparse
import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.html import escapejs
from django.utils.timezone import utc
from django.utils.translation import ugettext as _
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from pytz import timezone

from lily.deals.forms import CreateUpdateDealForm, CreateDealQuickbuttonForm
from lily.deals.models import Deal
from lily.utils.functions import is_ajax
from lily.utils.templatetags.messages import tag_mapping
from lily.utils.views import SortedListMixin, AjaxUpdateView,\
    DeleteBackAddSaveFormViewMixin, HistoryListViewMixin


class ListDealView(SortedListMixin, ListView):
    """
    Display a list of all deals.
    """
    model = Deal
    sortable = [1, 2, 3, 4, 5, 6, 7]
    default_order_by = 1


class DetailDealView(HistoryListViewMixin):
    """
    Display a detail page for a single deal.
    """
    model = Deal


class CreateUpdateDealView(DeleteBackAddSaveFormViewMixin):
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
        if self.object.stage in [1,3]:
            self.object.closed_date = datetime.datetime.utcnow().replace(tzinfo=utc)
        elif self.object.stage in [0,2]:
            self.object.closed_date = None
        self.object.save()

        return response

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        return '%s?order_by=7&sort_order=desc' % (reverse('deal_list'))


class CreateDealView(CreateUpdateDealView, CreateView):
    """
    View to add a deal.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to change the template to be rendered.
        """
        if is_ajax(request):
            self.template_name_suffix = '_form_ajax'
            self.form_class = CreateDealQuickbuttonForm

        return super(CreateDealView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Overloading super().form_valid to return json for an ajax request.
        """
        # Save instance
        response = super(CreateDealView, self).form_valid(form)

        # Show save message
        message = _('%s (Deal) has been saved.') % self.object.name
        messages.success(self.request, message)

        if is_ajax(self.request):
            # Reload when user is in the case list
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
        """
        Overloading super().form_invalid to return json for an ajax request.
        """
        response = self.render_to_response(self.get_context_data(form=form))
        if is_ajax(self.request):
            response = simplejson.dumps({
                'error': True,
                'html': response.rendered_content
            })
            return HttpResponse(response, mimetype='application/json')

        return response        


class UpdateDealView(CreateUpdateDealView, UpdateView):
    """
    View to edit a deal.
    """
    model = Deal

    def form_valid(self, form):
        """
        Overloading super().form_valid to show success message on edit.
        """
        # Save instance
        response = super(UpdateDealView, self).form_valid(form)

        # Show save message
        messages.success(self.request, _('%s (Deal) has been updated.') % self.object.name)

        return response


class DeleteDealView(DeleteView):
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
            # Return response
            if instance.closed_date is None:
                return HttpResponse(simplejson.dumps({}), mimetype='application/json')
            else:
                closed_date_local = instance.closed_date.astimezone(timezone(settings.TIME_ZONE))
                return HttpResponse(simplejson.dumps({'closed_date': closed_date_local.strftime('%d/%m/%Y %H:%M')}), mimetype='application/json')


# Perform logic here instead of in urls.py
create_deal_view = login_required(CreateDealView.as_view())
detail_deal_view = login_required(DetailDealView.as_view())
delete_deal_view = login_required(DeleteDealView.as_view())
update_deal_view = login_required(UpdateDealView.as_view())
list_deal_view = login_required(ListDealView.as_view())
update_stage_view = login_required(UpdateStageAjaxView.as_view())
