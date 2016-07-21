from django.conf.urls import url, include, patterns
from rest_framework.routers import DefaultRouter

from lily.accounts.api.views import AccountViewSet, AccountStatusViewSet
from lily.cases.api.views import CaseViewSet, CaseStatusList, CaseTypeList
from lily.contacts.api.views import ContactViewSet
from lily.deals.api.views import (DealViewSet, DealStatusViewSet, DealNextStepList, DealNextStepViewSet,
                                  DealWhyCustomerViewSet, DealContactedByViewSet, DealWhyLostViewSet,
                                  DealFoundThroughViewSet)
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
router.register(r'accounts/account', AccountViewSet)
router.register(r'accounts/statuses', AccountStatusViewSet)

router.register(r'tenants/tenant', TenantViewSet)
router.register(r'cases/case', CaseViewSet)
router.register(r'contacts/contact', ContactViewSet)

router.register(r'deals/deal', DealViewSet)
router.register(r'deals/next-steps', DealNextStepViewSet)
router.register(r'deals/why-customer', DealWhyCustomerViewSet)
router.register(r'deals/why-lost', DealWhyLostViewSet)
router.register(r'deals/found-through', DealFoundThroughViewSet)
router.register(r'deals/contacted-by', DealContactedByViewSet)
router.register(r'deals/statuses', DealStatusViewSet)

router.register(r'messaging/email/label', EmailLabelViewSet)
router.register(r'messaging/email/account', EmailAccountViewSet)
router.register(r'messaging/email/email', EmailMessageViewSet)
router.register(r'messaging/email/emailtemplate', EmailTemplateViewSet)
router.register(r'messaging/email/templatevariable', TemplateVariableViewSet)
router.register(r'messaging/email/shared_email_config', SharedEmailConfigViewSet)

router.register(r'users/user', LilyUserViewSet)
router.register(r'users/team', TeamViewSet)

router.register(r'notes/note', NoteViewSet)
router.register(r'utils/countries', CountryViewSet)

urlpatterns = patterns(
    '',
    url(r'^cases/statuses/$', CaseStatusList.as_view()),
    url(r'^cases/types/$', CaseTypeList.as_view()),

    url(r'^deals/nextsteps/$', DealNextStepList.as_view()),

    url(r'^utils/notifications/$', Notifications.as_view()),
    url(r'^utils/callername/$', CallerName.as_view()),
    url(r'^utils/apphash/$', AppHash.as_view()),

    url(r'^provide/dataprovider/$', DataproviderView.as_view()),

    url(r'^', include(router.urls)),
)
