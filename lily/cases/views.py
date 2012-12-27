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
from urlparse import urlparse

from lily.cases.forms import CreateUpdateCaseForm, AddCaseQuickbuttonForm
from lily.cases.models import Case
from lily.notes.views import NoteDetailViewMixin
from lily.utils.views import DeleteBackAddSaveFormViewMixin, SortedListMixin
from lily.utils.functions import is_ajax
from lily.utils.templatetags.messages import tag_mapping


class ListCaseView(SortedListMixin, ListView):
    """
    Display a list of all deals
    """
    template_name = 'cases/model_list.html'
    model = Case
    sortable = [1, 2, 3, 4, 5, 6]
    default_order_by = 1
    default_sort_order = SortedListMixin.DESC

    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to provide the list item template.
        """
        kwargs = super(ListCaseView, self).get_context_data(**kwargs)

        kwargs.update({
            'list_item_template': 'cases/model_list_item.html',
        })

        return kwargs


class DetailCaseView(NoteDetailViewMixin):
    """
    Display a detail page for a single deal.
    """
    template_name = 'cases/details.html'
    model = Case
    success_url_reverse_name = 'case_details'


class CreateUpdateCaseView(DeleteBackAddSaveFormViewMixin):
    """
    Base class for AddCaseView and EditCaseView.
    """
    template_name = 'cases/create_or_update.html'
    form_class = CreateUpdateCaseForm

    def get_success_url(self):
        """
        Get the url to redirect to after this form has succesfully been submitted.
        """
        return '%s?order_by=6&sort_order=desc' % (reverse('case_list'))


class AddCaseView(CreateUpdateCaseView, CreateView):
    """
    View to add a case.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to change the template to be rendered.
        """
        if is_ajax(request):
            self.template_name = 'cases/quickbutton_form.html'
            self.form_class = AddCaseQuickbuttonForm

        return super(AddCaseView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Overloading super().form_valid to show a success message after adding.
        """
        # Save instance
        super(AddCaseView, self).form_valid(form)

        message = _('%s (Case) has been saved.') % self.object.subject

        if is_ajax(self.request):
            # Redirect if in the list view
            url_obj = urlparse(self.request.META['HTTP_REFERER'])
            if url_obj.path.endswith(reverse('case_list')):
                # Show save message
                messages.success(self.request, message)

                do_redirect = True
                url = '%s?order_by=6&sort_order=desc' % reverse('case_list')
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

        return super(AddCaseView, self).form_invalid(form)


class EditCaseView(CreateUpdateCaseView, UpdateView):
    """
    View to edit a case.
    """
    model = Case

    def form_valid(self, form):
        """
        Overloading super().form_valid to add success message after editing.
        """
        # Save instance
        super(CreateUpdateCaseView, self).form_valid(form)

        # Show save message
        messages.success(self.request, _('%s (Case) has been edited.') % self.object.subject)

        return self.get_success_url()


class DeleteCaseView(DeleteView):
    """
    Delete an instance and all instances of m2m relationships.
    """
    model = Case
    http_method_names = ['post']

    def delete(self, request, *args, **kwargs):
        """
        Overloading super().delete to add a message of successful removal of this instance.
        """
        self.object = self.get_object()

        # Show delete message
        messages.success(self.request, _('%s (Case) has been deleted.') % self.object.subject)

        self.object.delete()

        return redirect(reverse('case_list'))


# Perform logic here instead of in urls.py
add_case_view = login_required(AddCaseView.as_view())
detail_case_view = login_required(DetailCaseView.as_view())
delete_case_view = login_required(DeleteCaseView.as_view())
edit_case_view = login_required(EditCaseView.as_view())
list_case_view = login_required(ListCaseView.as_view())
