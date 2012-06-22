from urlparse import urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.html import escapejs
from django.utils.translation import ugettext as _
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from lily.deals.forms import AddDealForm, AddDealQuickbuttonForm, EditDealForm
from lily.deals.models import Deal
from lily.utils.functions import is_ajax
from lily.utils.templatetags.messages import tag_mapping
from lily.utils.views import DetailNoteFormView, SortedListMixin


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


class DetailDealView(DetailNoteFormView):
    """
    Display a detail page for a single deal.
    """
    template_name = 'deals/details.html'
    model = Deal
    success_url_reverse_name = 'deal_details'
    

class AddDealView(CreateView):
    """
    View to add a deal.
    """
    template_name = 'deals/create_or_update.html'
    form_class = AddDealForm
    
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
        
        if is_ajax(self.request):
            message = _('%s (Deal) has been saved.') % self.object.name
            
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
        else:
            # Show save message
            messages.success(self.request, _('%s (Deal) has been saved.') % self.object.name)
        
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

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        return redirect('%s?order_by=7&sort_order=desc' % (reverse('deal_list')))


class EditDealView(UpdateView):
    """
    View to edit a deal.
    """
    template_name = 'deals/create_or_update.html'
    form_class = EditDealForm
    model = Deal
    
    def form_valid(self, form):
        """
        Overloading super().form_valid to add success message after editing.
        """
        # Save instance
        super(EditDealView, self).form_valid(form)
        
        # Show save message
        messages.success(self.request, _('%s (Deal) has been edited.') % self.object.name);
            
        return self.get_success_url()
    
    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        return redirect('%s?order_by=7&sort_order=desc' % (reverse('deal_list')))


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


# Perform logic here instead of in urls.py
add_deal_view = login_required(AddDealView.as_view())
detail_deal_view = login_required(DetailDealView.as_view())
delete_deal_view = login_required(DeleteDealView.as_view())
edit_deal_view = login_required(EditDealView.as_view())
list_deal_view = login_required(ListDealView.as_view())
