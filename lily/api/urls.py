from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from lily.accounts.api.views import AccountViewSet, AccountStatusViewSet
from lily.calls.api.views import CallViewSet
from lily.cases.api.views import CaseViewSet, CaseStatusViewSet, CaseTypeList
from lily.contacts.api.views import ContactViewSet
from lily.deals.api.views import (DealViewSet, DealStatusViewSet, DealNextStepList, DealNextStepViewSet,
                                  DealWhyCustomerViewSet, DealContactedByViewSet, DealWhyLostViewSet,
                                  DealFoundThroughViewSet)
from lily.integrations.api.views import DocumentDetails, PandaDocAuth, PandaDocList
from lily.messaging.email.api.views import (EmailLabelViewSet, EmailAccountViewSet, EmailMessageViewSet,
                                            EmailTemplateViewSet, SharedEmailConfigViewSet,
                                            TemplateVariableViewSet)
from lily.notes.api.views import NoteViewSet
from lily.provide.api.views import DataproviderView
from lily.tenant.api.views import TenantViewSet
from lily.users.api.views import LilyUserViewSet, TeamViewSet
from lily.utils.api.views import AppHash, CallerName, CountryViewSet, Notifications

# Define routes, using the default router so the API is browsable.
router = DefaultRouter()

router.register(r'accounts/statuses', AccountStatusViewSet)
router.register(r'accounts', AccountViewSet)

router.register(r'calls', CallViewSet)

router.register(r'cases/statuses', CaseStatusViewSet)
router.register(r'cases', CaseViewSet)

router.register(r'contacts', ContactViewSet)

router.register(r'deals/next-steps', DealNextStepViewSet)
router.register(r'deals/why-customer', DealWhyCustomerViewSet)
router.register(r'deals/why-lost', DealWhyLostViewSet)
router.register(r'deals/found-through', DealFoundThroughViewSet)
router.register(r'deals/contacted-by', DealContactedByViewSet)
router.register(r'deals/statuses', DealStatusViewSet)
router.register(r'deals', DealViewSet)

router.register(r'messaging/email/labels', EmailLabelViewSet)
router.register(r'messaging/email/accounts', EmailAccountViewSet)
router.register(r'messaging/email/email', EmailMessageViewSet)
router.register(r'messaging/email/templates', EmailTemplateViewSet)
router.register(r'messaging/email/template-variables', TemplateVariableViewSet)
router.register(r'messaging/email/shared-email-configurations', SharedEmailConfigViewSet)

router.register(r'notes', NoteViewSet)

router.register(r'users/team', TeamViewSet)
router.register(r'users', LilyUserViewSet)

router.register(r'tenants', TenantViewSet)

router.register(r'utils/countries', CountryViewSet)

urlpatterns = [
    url(r'^cases/types/$', CaseTypeList.as_view()),

    url(r'^deals/nextsteps/$', DealNextStepList.as_view()),

    url(r'integrations/auth/pandadoc$', PandaDocAuth.as_view()),
    url(r'integrations/documents/(?P<contact_id>[0-9]+)/$', PandaDocList.as_view()),
    url(r'integrations/documents/(?P<document_id>.+)/$', DocumentDetails.as_view()),

    url(r'^utils/notifications/$', Notifications.as_view()),
    url(r'^utils/callername/$', CallerName.as_view()),
    url(r'^utils/apphash/$', AppHash.as_view()),

    url(r'^provide/dataprovider/$', DataproviderView.as_view()),

    url(r'^', include(router.urls)),
]
