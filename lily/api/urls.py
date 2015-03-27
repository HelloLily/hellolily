from rest_framework import routers

from lily.contacts.api.views import ContactViewSet

router = routers.DefaultRouter()
router.register(r'contacts', ContactViewSet)
