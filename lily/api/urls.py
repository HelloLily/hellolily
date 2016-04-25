from django.conf.urls import url, include, patterns
from rest_framework.routers import DefaultRouter

from lily.accounts.api.views import (AccountViewSet, AccountAddressViewSet, AccountEmailAddressViewSet,
                                     AccountPhoneNumberViewSet, AccountTagViewSet, WebsiteViewSet,
                                     AccountStatusViewSet)
from lily.cases.api.views import CaseViewSet, CaseStatusList, CaseTypeList
from lily.contacts.api.views import ContactViewSet
from lily.deals.api.views import (DealViewSet, DealStatusViewSet, DealNextStepList, DealNextStepViewSet,
                                  DealWhyCustomerViewSet, DealContactedByViewSet, DealWhyLostViewSet,
                                  DealFoundThroughViewSet)
from lily.messaging.email.api.views import (EmailLabelViewSet, EmailAccountViewSet, EmailMessageViewSet,
                                            EmailTemplateViewSet, SharedEmailConfigViewSet,
                                            TemplateVariableViewSet)
from lily.notes.api.views import NoteViewSet
from lily.tenant.api.views import TenantViewSet
from lily.users.api.views import LilyUserViewSet, TeamViewSet
from lily.utils.api.views import CountryViewSet, CallerName, Notifications

from .routers import SimpleRouter, NestedSimpleRouter


# Define the account routes, using the simple router with support for nested routes.
# TODO: make the account api relational so this can be refactored.
simple_router = SimpleRouter()

simple_router.register(r'accounts/account', AccountViewSet)
accounts_router = NestedSimpleRouter(simple_router, r'accounts/account', lookup='object')
accounts_router.register(r'phone_numbers', AccountPhoneNumberViewSet)
accounts_router.register(r'addresses', AccountAddressViewSet)
accounts_router.register(r'email_addresses', AccountEmailAddressViewSet)
accounts_router.register(r'websites', WebsiteViewSet)
accounts_router.register(r'tags', AccountTagViewSet)

# Define routes, using the default router so the API is browsable.
router = DefaultRouter()

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

router.register(r'notes', NoteViewSet)
router.register(r'utils/countries', CountryViewSet)

urlpatterns = patterns(
    '',
    url(r'^cases/statuses/$', CaseStatusList.as_view()),
    url(r'^cases/types/$', CaseTypeList.as_view()),

    url(r'^deals/nextsteps/$', DealNextStepList.as_view()),

    url(r'^utils/notifications/$', Notifications.as_view()),
    url(r'^utils/callername/$', CallerName.as_view()),

    url(r'^', include(router.urls)),
    url(r'^', include(simple_router.urls)),
    url(r'^', include(accounts_router.urls)),
)
