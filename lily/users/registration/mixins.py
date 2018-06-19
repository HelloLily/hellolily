from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView

from lily.users.models import UserInfo


class RegistrationMixin(FormView):
    """
    Mixin that saves the current step in the session or redirects to the smart redirect view.
    """
    step = None
    step_name = None
    step_count = None

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.user.info.registration_finished:
                # The user has finished the registration already.
                return HttpResponseRedirect(reverse('base_view'))
            elif self.step_name == 'auth' or self.step_name == 'verify_email':
                # Authenticated users don't need to fill in auth credentials or verify their email.
                # Redirect them to the success_url.
                return HttpResponseRedirect(self.get_success_url())
            elif self.step_name == 'done':
                # The registration process is done, so clean up the session and save this info to the db.
                del self.request.session[settings.REGISTRATION_SESSION_KEY]
                self.request.user.info.registration_finished = True
                self.request.user.info.email_account_status = UserInfo.COMPLETE
                self.request.user.info.save()

        elif not (self.step_name == 'auth' or self.step_name == 'verify_email'):
            # User is not authenticated and is not on step 1 or 2, that are only steps they may be on right now.
            return HttpResponseRedirect(reverse('register_auth'))
        elif self.step_name == 'verify_email' and \
                not self.request.session[settings.REGISTRATION_SESSION_KEY].get('auth_data'):
            # Something is wrong with the session, so redirect to step 1.
            return HttpResponseRedirect(reverse('register_auth'))

        # User is authenticated, but has not finished registration.
        if settings.REGISTRATION_SESSION_KEY in request.session:
            current_step = request.session[settings.REGISTRATION_SESSION_KEY]['step']

            # User may request step 1 if they're on step 2, maybe they want to register another way?
            if self.step < current_step and current_step > 2:
                # The user has requested an earlier step than where he/she was.
                # Redirect to the view that determines correct step.
                return HttpResponseRedirect(reverse('register'))
        else:
            # If the session key is not present, initialize the session dict.
            request.session[settings.REGISTRATION_SESSION_KEY] = {}

        # The user has requested current or next step, so store new values in the session.
        request.session[settings.REGISTRATION_SESSION_KEY]['step'] = self.step
        request.session[settings.REGISTRATION_SESSION_KEY]['step_name'] = self.step_name

        return super(RegistrationMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RegistrationMixin, self).get_context_data(**kwargs)

        context.update({
            'current_step': self.step,
            'step_count': self.step_count,
        })

        return context
