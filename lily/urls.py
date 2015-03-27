import os

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView

from lily.accounts.api.views import AccountViewSet
from lily.api.urls import router
from lily.cases.api.views import CaseList, UserCaseList, TeamsCaseList, CaseStatusList
from lily.deals.api.views import DealList, DealCommunicationList, DealWonWrittenList, DealStagesList
from lily.messaging.email.api.views import (EmailLabelViewSet, EmailAccountViewSet, EmailMessageViewSet,
                                            EmailTemplateViewSet)
from lily.users.api.views import TeamList, LilyUserViewSet
from lily.utils.views import LoginRequiredRootView
from lily.utils.api.views import Queues

admin.autodiscover()


# Routers provide an easy way of automatically determining the URL conf.
router.register(r'accounts/account', AccountViewSet)
router.register(r'messaging/email/label', EmailLabelViewSet)
router.register(r'messaging/email/account', EmailAccountViewSet)
router.register(r'messaging/email/email', EmailMessageViewSet)
router.register(r'messaging/email/emailtemplate', EmailTemplateViewSet)
router.register(r'users/user', LilyUserViewSet)

urlpatterns = patterns(
    '',
    url(r'^accounts/', include('lily.accounts.urls', app_name='accounts')),
    url(r'^contacts/', include('lily.contacts.urls', app_name='contacts')),
    url(r'^cases/', include('lily.cases.urls', app_name='cases')),
    url(r'^deals/', include('lily.deals.urls', app_name='deals')),
    url(r'^notes/', include('lily.notes.urls')),
    url(r'^messaging/', include('lily.messaging.urls')),
    url(r'^provide/', include('lily.provide.urls')),
    url(r'^updates/', include('lily.updates.urls')),
    url(r'^', include('lily.users.urls')),
    url(r'^', include('lily.utils.urls')),
    url(r'^taskmonitor/', include('taskmonitor.urls')),
    url(r'^search/', include('lily.search.urls')),

    # Django admin urls
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Django rest
    url(r'^api/', include(router.urls)),
    url(r'^api/cases/$', CaseList.as_view()),
    url(r'^api/cases/teams/$', TeamsCaseList.as_view()),
    url(r'^api/cases/teams/(?P<pk>[0-9]+)/$', TeamsCaseList.as_view()),
    url(r'^api/cases/user/$', UserCaseList.as_view()),
    url(r'^api/cases/user/(?P<pk>[0-9]+)/$', UserCaseList.as_view()),
    url(r'^api/cases/statuses/$', CaseStatusList.as_view()),
    url(r'^api/deals/stages', DealStagesList.as_view()),
    url(r'^api/deals/stats/communication', DealCommunicationList.as_view()),
    url(r'^api/deals/stats/wonwritten', DealWonWrittenList.as_view()),
    url(r'^api/deals', DealList.as_view()),
    url(r'^api/users/teams/$', TeamList.as_view()),
    url(r'^api/utils/queues/(?P<queue>[\w]+)/$', Queues.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    (r'^$', LoginRequiredRootView.as_view()),

    (r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    (r'^favicon\.ico$', RedirectView.as_view(url=settings.STATIC_URL + 'lily/images/core/favicon.ico')),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('', url(r'^__debug__/', include(debug_toolbar.urls)), )

# Works only in debug mode
if os.environ.get('PRODUCTION_MEDIA_URL', None) is None:
    urlpatterns += patterns(
        '',
        (r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )
