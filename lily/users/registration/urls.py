from django.conf.urls import url

from .views import (
    RegisterRedirectView, RegisterAuthView, RegisterVerifyEmailView, RegisterProfileView,
    RegisterEmailAccountSetupView, RegisterEmailAccountDetailsView, RegisterDoneView, AcceptInvitationView
)

# Define the view flow for registration.
registration_flow = (
    RegisterAuthView,
    RegisterVerifyEmailView,
    RegisterProfileView,
    RegisterEmailAccountSetupView,
    RegisterEmailAccountDetailsView,
    RegisterDoneView,
)

# Loop over the steps in the registration flow and create a Django RegexURLPattern for each step.
registration_steps = [
    url(
        regex=r'^step-{}/$'.format(step_number),
        view=step_view.as_view(
            step=step_number,
            step_count=len(registration_flow),
        ),
        name='register_{}'.format(step_view.step_name)
    ) for step_number, step_view in enumerate(registration_flow, start=1)
]

# Actually register the urls to Django.
urlpatterns = [
    url(regex=r'^$', view=RegisterRedirectView.as_view(), name='register'),
    url(  # yapf: disable
        regex=r'^invitation/accept/(?P<first_name>.+)/(?P<email>.+)/(?P<tenant_id>[0-9]+)-(?P<date>[0-9]+)-(?P<hash>.+)/$',  # noqa
        view=AcceptInvitationView.as_view(),
        name='invitation_accept',
    ),
] + registration_steps
