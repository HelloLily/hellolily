from django_elasticsearch_dsl import DocType, Index, IntegerField, KeywordField, TextField

from .models import LilyUser

user_index = Index('user')


@user_index.doc_type
class LilyUserDoc(DocType):
    email = TextField()
    full_name = TextField()
    internal_number = KeywordField()
    phone_number = TextField()
    position = TextField()
    tenant_id = IntegerField()

    class Meta:
        model = LilyUser
