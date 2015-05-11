from lily.accounts.api.views import (AccountViewSet, AccountAddressViewSet, AccountEmailAddressViewSet,
                                     AccountPhoneNumberViewSet, AccountTagViewSet, WebsiteViewSet,)
from lily.contacts.api.views import ContactViewSet
from lily.notes.api.views import NoteViewSet
from .routers import SimpleRouter, NestedSimpleRouter

router = SimpleRouter()
router.register(r'accounts/account', AccountViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'notes', NoteViewSet)

accounts_router = NestedSimpleRouter(router, r'accounts/account', lookup='object')
accounts_router.register(r'phone_numbers', AccountPhoneNumberViewSet)
accounts_router.register(r'addresses', AccountAddressViewSet)
accounts_router.register(r'email_addresses', AccountEmailAddressViewSet)
accounts_router.register(r'websites', WebsiteViewSet)
accounts_router.register(r'tags', AccountTagViewSet)
