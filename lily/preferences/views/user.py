from braces.views import StaticContextMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import UpdateView
from django.utils.translation import ugettext_lazy as _

from lily.preferences.forms.user import UserAccountForm
from lily.utils.views import LoginRequiredMixin


class UserAccountView(LoginRequiredMixin, SuccessMessageMixin, StaticContextMixin, UpdateView):
    form_class = UserAccountForm
    template_name = 'form.html'
    static_context = {'form_prevent_autofill': True}

    def get_success_message(self, cleaned_data):
        return _('%(name)s has been updated' % {'name': self.object.full_name})

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return '/#/preferences/user/account'
