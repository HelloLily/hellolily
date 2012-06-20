from django.db import models
from polymorphic import PolymorphicModel
from django_extensions.db.models import TimeStampedModel

class Message(PolymorphicModel, TimeStampedModel):
    datetime = models.DateTimeField()
    is_seen = models.BooleanField(default=False)