from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.views.generic.edit import CreateView, DeleteView
from django.utils import simplejson
from django.utils.html import escapejs
from django.utils.translation import ugettext as _

from lily.updates.forms import CreateBlogEntryForm
from lily.updates.models import BlogEntry
from lily.tenant.middleware import get_current_user
from lily.utils.functions import is_ajax


class AddBlogEntryView(CreateView):
    form_class = CreateBlogEntryForm
    model = BlogEntry

    def form_valid(self, form):
        """
        When adding a blogentry, try to automatically save the author and object being replied to.
        """
        blogentry = form.save(commit=False)
        blogentry.author = self.request.user
        try:
            blogentry.reply_to = BlogEntry.objects.get(pk=self.request.POST['reply_to'])
        except:
            pass
        blogentry.save()

        # Show success message
        messages.success(self.request, _('Post successful.'))

        return super(AddBlogEntryView, self).form_valid(form)

    def get_success_url(self):
        return reverse('dashboard')


class DeleteBlogEntryView(DeleteView):
    model = BlogEntry
    http_method_names = ['post']

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
            return HttpResponse(simplejson.dumps({
                'error': False,
                'redirect': do_redirect,
                'url': url
            }), mimetype='application/json')

        return redirect(request.META.get('HTTP_REFERER', reverse('dashboard')))


delete_blogentry_view = login_required(DeleteBlogEntryView.as_view())
