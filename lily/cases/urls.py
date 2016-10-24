from django.conf.urls import url

from .views import DeleteCaseView


urlpatterns = [
    url(r'^delete/(?P<pk>[\w-]+)/$', DeleteCaseView.as_view(), name='case_delete'),
]
