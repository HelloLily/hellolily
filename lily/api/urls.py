from rest_framework import routers

from lily.contacts.api.views import ContactViewSet
from lily.notes.api.views import NoteViewSet

router = routers.DefaultRouter()
router.register(r'contacts', ContactViewSet)
router.register(r'notes', NoteViewSet)
