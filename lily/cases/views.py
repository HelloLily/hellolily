import anyjson
from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import DeleteView

from lily.utils.views.mixins import LoginRequiredMixin

from .models import Case


class DeleteCaseView(LoginRequiredMixin, DeleteView):
    """
    Delete an instance and all instances of m2m relationships.
    """
    model = Case

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        # Show delete message
        messages.success(self.request, _('%s (Case) has been deleted.') % self.object.subject)

        response = anyjson.serialize({
            'error': False,
        })
        return HttpResponse(response, content_type='application/json')
