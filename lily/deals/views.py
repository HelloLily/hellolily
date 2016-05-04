import anyjson
from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import DeleteView

from lily.utils.views.mixins import LoginRequiredMixin

from .models import Deal


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

        response = anyjson.serialize({
            'error': False,
            'redirect_url': redirect_url
        })
        return HttpResponse(response, content_type='application/json')

    def get_success_url(self):
        return '/#/deals'
