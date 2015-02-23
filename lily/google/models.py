from django.db import models
from oauth2client.django_orm import FlowField

from lily.users.models import LilyUser


class FlowModel(models.Model):
    """
    FlowModel stores temporary the flow information for authenticating
    a user for the Google APIs
    """
    id = models.ForeignKey(LilyUser, primary_key=True)
    flow = FlowField()
