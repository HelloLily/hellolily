from urlparse import urlparse
import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
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

from lily.deals.forms import CreateUpdateDealForm, AddDealQuickbuttonForm
from lily.deals.models import Deal
from lily.notes.views import NoteDetailViewMixin
from lily.utils.functions import is_ajax
from lily.utils.templatetags.messages import tag_mapping
from lily.utils.views import SortedListMixin, AjaxUpdateView,\
    DeleteBackAddSaveFormViewMixin


class ListDealView(SortedListMixin, ListView):
    """
    Display a list of all deals
    """
    template_name = 'deals/model_list.html'
    model = Deal
    sortable = [1, 2, 3, 4, 5, 6, 7]
    default_order_by = 1

    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to provide the list item template.
        """
        kwargs = super(ListDealView, self).get_context_data(**kwargs)

        kwargs.update({
            'list_item_template': 'deals/model_list_item.html',
        })
        
        return kwargs


class DetailDealView(NoteDetailViewMixin):
    """
    Display a detail page for a single deal.
    """
    template_name = 'deals/details.html'
    model = Deal
    success_url_reverse_name = 'deal_details'
    

class CreateUpdateDealView(DeleteBackAddSaveFormViewMixin):
    """
    Base class for AddDealView and EditDealView.
    """
    template_name = 'deals/create_or_update.html'
    form_class = CreateUpdateDealForm
    
    def form_valid(self, form):
        """
        Overloading super().form_valid to add success message after editing.
        """
        # Save instance
        super(EditDealView, self).form_valid(form)
        
        # Set closed_date after changing stage to lost/won and reset it when it's new/pending
        if self.object.stage in [1,3]:
            self.object.closed_date = datetime.datetime.utcnow().replace(tzinfo=utc)
        elif self.object.stage in [0,2]:
            self.object.closed_date = None
        self.object.save()
        
        # Show save message
        messages.success(self.request, _('%s (Deal) has been edited.') % self.object.name);
            
        return self.get_success_url()
    
    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        return redirect('%s?order_by=7&sort_order=desc' % (reverse('deal_list')))
    
class AddDealView(CreateUpdateDealView, CreateView):
    """
    View to add a deal.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to change the template to be rendered.
        """
        if is_ajax(request):
            self.template_name = 'deals/quickbutton_form.html'
            self.form_class = AddDealQuickbuttonForm
        
        return super(AddDealView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Overloading super().form_valid to return json for an ajax request.
        """
        # Save instance
        super(AddDealView, self).form_valid(form)
        
        message = _('%s (Deal) has been saved.') % self.object.name
        
        if is_ajax(self.request):
            # Redirect if in the list view
            url_obj = urlparse(self.request.META['HTTP_REFERER'])
            if url_obj.path.endswith(reverse('deal_list')):
                # Show save message
                messages.success(self.request, message)

                do_redirect = True
                url = '%s?order_by=7&sort_order=desc' % reverse('deal_list')
                notification = False
                html_response = ''
            else:
                do_redirect = False
                url = ''
                html_response = ''
                notification = [{ 'message': escapejs(message), 'tags': tag_mapping.get('success') }]
            
            # Return response
            return HttpResponse(simplejson.dumps({
                'error': False,
                'html': html_response,
                'redirect': do_redirect,
                'notification': notification,
                'url': url
            }), mimetype='application/json')

        # Show save message
        messages.success(self.request, message)
        
        return self.get_success_url()

    def form_invalid(self, form):
        """
        Overloading super().form_invalid to return json for an ajax request.
        """
        if is_ajax(self.request):
            context = RequestContext(self.request, self.get_context_data(form=form))
            return HttpResponse(simplejson.dumps({
                'error': True,
                'html': render_to_string(self.template_name, context_instance=context)
            }), mimetype='application/json')
        
        return super(AddDealView, self).form_invalid(form)


class EditDealView(CreateUpdateDealView, UpdateView):
    """
    View to edit a deal.
    """
    model = Deal


class DeleteDealView(DeleteView):
    """
    Delete an instance and all instances of m2m relationships.
    """
    model = Deal
    http_method_names = ['post']

    def delete(self, request, *args, **kwargs):
        """
        Overloading super().delete to add a message of successful removal of this instance.
        """
        self.object = self.get_object()
        
        # Show delete message
        messages.success(self.request, _('%s (Deal) has been deleted.') % self.object.name);

        self.object.delete()

        return redirect(reverse('deal_list'))


class EditStageAjaxView(AjaxUpdateView):
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
                
                if instance.stage in [1,3]:
                    instance.closed_date = datetime.datetime.utcnow().replace(tzinfo=utc)
                elif instance.stage in [0,2]:
                    instance.closed_date = None
                    
                instance.save() 
            else:
                raise Http404();
        except:
            raise Http404()
        else:
            # Return response
            if instance.closed_date is None:
                return HttpResponse(simplejson.dumps({}), mimetype='application/json')
            else:
                closed_date_local = instance.closed_date.astimezone(timezone(settings.TIME_ZONE))
                return HttpResponse(simplejson.dumps({ 'closed_date': closed_date_local.strftime('%d/%m/%Y %H:%M') }), mimetype='application/json')


# Perform logic here instead of in urls.py
add_deal_view = login_required(AddDealView.as_view())
detail_deal_view = login_required(DetailDealView.as_view())
delete_deal_view = login_required(DeleteDealView.as_view())
edit_deal_view = login_required(EditDealView.as_view())
list_deal_view = login_required(ListDealView.as_view())
edit_stage_view = login_required(EditStageAjaxView.as_view())
