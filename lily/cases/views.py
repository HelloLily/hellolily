from urlparse import urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from lily.cases.forms import CreateUpdateCaseForm, CreateCaseQuickbuttonForm
from lily.cases.models import Case
from lily.utils.functions import is_ajax
from lily.utils.views import SortedListMixin, HistoryListViewMixin


class ListCaseView(SortedListMixin, ListView):
    """
    Display a list of cases.
    """
    model = Case
    sortable = [1, 2, 3, 4, 5, 6]
    default_order_by = 1
    default_sort_order = SortedListMixin.DESC


class DetailCaseView(HistoryListViewMixin):
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
        return '%s?order_by=6&sort_order=desc' % (reverse('case_list'))


class CreateCaseView(CreateUpdateCaseView, CreateView):
    def dispatch(self, request, *args, **kwargs):
        """
        For AJAX calls, use a different form and template.
        """
        if is_ajax(request):
            self.template_name_suffix = '_form_ajax'
            self.form_class = CreateCaseQuickbuttonForm

        return super(CreateCaseView, self).dispatch(request, *args, **kwargs)

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
                redirect_url = '%s?order_by=6&sort_order=desc' % reverse('case_list')

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


class UpdateCaseView(CreateUpdateCaseView, UpdateView):
    model = Case

    def form_valid(self, form):
        # Saves the instance
        response = super(UpdateCaseView, self).form_valid(form)

        # Show save message
        messages.success(self.request, _('%s (Case) has been updated.') % self.object.subject)

        return response


class DeleteCaseView(DeleteView):
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


# Perform logic here instead of in urls.py
create_case_view = login_required(CreateCaseView.as_view())
detail_case_view = login_required(DetailCaseView.as_view())
delete_case_view = login_required(DeleteCaseView.as_view())
update_case_view = login_required(UpdateCaseView.as_view())
list_case_view = login_required(ListCaseView.as_view())
