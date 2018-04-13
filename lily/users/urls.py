from django.conf.urls import url, include

urlpatterns = [
    url(
        regex=r'^',
        view=include('lily.users.authentication.urls'),
    ),
    url(
        regex=r'^two-factor/',
        view=include('lily.users.two_factor_auth.urls'),
    ),
    url(
        regex=r'^register/',
        view=include('lily.users.registration.urls'),
    ),
]
