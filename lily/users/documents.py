from django_elasticsearch_dsl import DocType, Index, IntegerField

from lily.search.fields import CharField, EmailAddressField, PhoneNumberField
from .models import LilyUser

user_index = Index('user')


@user_index.doc_type
class LilyUserDoc(DocType):
    email = EmailAddressField()
    full_name = CharField()
    phone_number = PhoneNumberField()
    position = CharField()
    tenant_id = IntegerField()

    class Meta:
        model = LilyUser
