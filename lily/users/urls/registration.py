from django.conf.urls import url


from lily.users.views.registration import (
    AcceptInvitationView, RegistrationView, ActivationView, ActivationResendView, SendInvitationView,
    ConfirmationView
)


registration_urls = [
    url(
        regex=r'^invitation/invite/$',
        view=SendInvitationView.as_view(),
        name='invitation_invite',
    ),
    url(
        regex=r'^invitation/accept/(?P<first_name>.+)/(?P<email>.+)/(?P<tenant_id>[0-9]+)-(?P<date>[0-9]+)-(?P<hash>.+)/$',  # noqa
        view=AcceptInvitationView.as_view(),
        name='invitation_accept',
    ),

    url(
        regex=r'^register/$',
        view=RegistrationView.as_view(),
        name='register',
    ),

    url(
        regex=r'^register/confirmation/$',
        view=ConfirmationView.as_view(),
        name='confirmation'),

    url(
        regex=r'^activation/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        view=ActivationView.as_view(),
        name='activation',
    ),
    url(
        regex=r'^activation/resend/$',
        view=ActivationResendView.as_view(),
        name='activation_resend',
    ),
]
