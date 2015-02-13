from django.db import models
from oauth2client.django_orm import FlowField
from south.modelsinspector import add_introspection_rules

from lily.users.models import LilyUser


class FlowModel(models.Model):
    """
    FlowModel stores temporary the flow information for authenticating
    a user for the Google APIs
    """
    id = models.ForeignKey(LilyUser, primary_key=True)
    flow = FlowField()


add_introspection_rules([], ["^oauth2client\.django_orm\.FlowField"])
add_introspection_rules([], ["^oauth2client\.django_orm\.CredentialsField"])
