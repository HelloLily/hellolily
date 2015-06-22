from lily.accounts.api.views import (AccountViewSet, AccountAddressViewSet, AccountEmailAddressViewSet,
                                     AccountPhoneNumberViewSet, AccountTagViewSet, WebsiteViewSet)
from lily.cases.api.views import CaseViewSet
from lily.contacts.api.views import ContactViewSet
from lily.deals.api.views import DealViewSet
from lily.messaging.email.api.views import (EmailLabelViewSet, EmailAccountViewSet, EmailMessageViewSet,
                                            EmailTemplateViewSet)
from lily.notes.api.views import NoteViewSet
from lily.users.api.views import LilyUserViewSet, TeamViewSet

from .routers import SimpleRouter, NestedSimpleRouter

# Routers provide an easy way of automatically determining the URL conf.
router = SimpleRouter()

router.register(r'accounts/account', AccountViewSet)
accounts_router = NestedSimpleRouter(router, r'accounts/account', lookup='object')
accounts_router.register(r'phone_numbers', AccountPhoneNumberViewSet)
accounts_router.register(r'addresses', AccountAddressViewSet)
accounts_router.register(r'email_addresses', AccountEmailAddressViewSet)
accounts_router.register(r'websites', WebsiteViewSet)
accounts_router.register(r'tags', AccountTagViewSet)

router.register(r'cases/case', CaseViewSet)
router.register(r'contacts/contact', ContactViewSet)
router.register(r'deals/deal', DealViewSet)

router.register(r'messaging/email/label', EmailLabelViewSet)
router.register(r'messaging/email/account', EmailAccountViewSet)
router.register(r'messaging/email/email', EmailMessageViewSet)
router.register(r'messaging/email/emailtemplate', EmailTemplateViewSet)

router.register(r'users/user', LilyUserViewSet)
router.register(r'users/team', TeamViewSet)

router.register(r'notes', NoteViewSet)
