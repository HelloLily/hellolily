import anyjson

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.edit import CreateView, DeleteView
from django.utils.translation import ugettext as _

from lily.updates.forms import CreateBlogEntryForm
from lily.updates.models import BlogEntry
from lily.tenant.middleware import get_current_user
from lily.utils.functions import is_ajax


class AddBlogEntryView(CreateView):
    form_class = CreateBlogEntryForm
    model = BlogEntry
    
    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to change the template to be rendered for ajax requests.
        """
        # Change form and template for ajax calls or create formset instances for the normal form
        self.reply_to = None
        if kwargs.get('pk'):
            self.reply_to = get_object_or_404(BlogEntry, pk=kwargs.get('pk'))

        if is_ajax(request):
            self.template_name_suffix = '_form_ajax'
        
        return super(AddBlogEntryView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        When adding a blogentry, try to automatically save the author and object being replied to.
        """
        blogentry = form.save(commit=False)
        blogentry.author = self.request.user

        if self.reply_to:
            blogentry.reply_to = self.reply_to

        blogentry.save()

        # Show success message
        messages.success(self.request, _('Post successful.'))

        if is_ajax(self.request):
            response = anyjson.serialize({
                'error': False,
                'redirect_url': reverse('dashboard')
            })
            return HttpResponse(response, mimetype='application/json')

        return super(AddBlogEntryView, self).form_valid(form)

    def form_invalid(self, form):
        response = self.render_to_response(self.get_context_data(form=form))
        if is_ajax(self.request):
            response = anyjson.serialize({
                'error': True,
                'html': response.rendered_content
            })
            return HttpResponse(response, mimetype='application/json')

        return response

    def get_context_data(self, **kwargs):
        context = super(AddBlogEntryView, self).get_context_data(**kwargs)
        context.update({
            'reply_to': self.reply_to or None
        })
        return context

    def get_success_url(self):
        return reverse('dashboard')


class DeleteBlogEntryView(DeleteView):
    model = BlogEntry

    def delete(self, request, *args, **kwargs):
        """
        Overloading super().delete to check if the user who tries to delete this entry is also the
        author.
        """
        self.object = self.get_object()

        # Check if this blog entry account is written by request.user
        if self.object.author != get_current_user():
            raise Http404()

        # Show delete message
        messages.success(self.request, _('Post deleted.'))

        self.object.delete()

        if is_ajax(request):
            do_redirect = True
            url = request.META.get('HTTP_REFERER', reverse('dashboard'))

            # Return response
            return HttpResponse(anyjson.serialize({
                'error': False,
                'redirect_url': url
            }), mimetype='application/json')

        return redirect(request.META.get('HTTP_REFERER', reverse('dashboard')))


add_blogentry_view = login_required(AddBlogEntryView.as_view())
delete_blogentry_view = login_required(DeleteBlogEntryView.as_view())
