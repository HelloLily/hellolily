from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.views import password_reset_confirm, password_reset
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from lily.utils.views import RedirectSetMessageView
from lily.users.forms.password_reset import CustomPasswordResetForm, CustomSetPasswordForm

password_reset_urls = [
    url(
        regex=r'^password_reset/$',
        view=password_reset,
        kwargs={
            'email_template_name': 'email/password_reset.email',
            'template_name': 'users/password_reset/form.html',
            'password_reset_form': CustomPasswordResetForm,
            'from_email': settings.DEFAULT_FROM_EMAIL,
        },
        name='password_reset',
    ),
    url(
        regex=r'^password_reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        view=password_reset_confirm,
        kwargs={
            'template_name': 'users/password_reset/confirm.html',
            'set_password_form': CustomSetPasswordForm
        },
        name='password_reset_confirm',
    ),
    url(
        regex=r'^password_reset/done/$',
        view=RedirectSetMessageView.as_view(
            url=reverse_lazy('login'),
            message_level='info',
            message=_('I\'ve sent you an email, please check it to reset your password.'),
            permanent=False
        ),
        name='password_reset_done'),
    url(
        regex=r'^password_reset/complete/$',
        view=RedirectSetMessageView.as_view(
            url=reverse_lazy('login'),
            message_level='info',
            message=_('I\'ve reset your password, please login.'),
            permanent=False
        ),
        name='password_reset_complete',
    ),
]
