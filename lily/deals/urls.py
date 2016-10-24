from django.conf.urls import url

from .views import DeleteDealView

urlpatterns = [
    url(r'^delete/(?P<pk>[\w-]+)/$', DeleteDealView.as_view(), name='deal_delete'),
]
