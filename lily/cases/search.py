from django_elasticsearch_dsl import DocType, Index, IntegerField, TextField

from .models import Case

index = Index('case')


@index.doc_type
class CaseDoc(DocType):
    account = TextField()
    assigned_to = TextField()
    contact = TextField()
    created_by = TextField()
    status = TextField()
    subject = TextField()
    tags = TextField()
    tenant_id = IntegerField()
    type = TextField()

    def prepare_account(self, obj):
        return obj.account.name if obj.account else None

    def prepare_assigned_to(self, obj):
        return obj.assigned_to.full_name if obj.assigned_to else None

    def prepare_contact(self, obj):
        return obj.contact.full_name if obj.contact else None

    def prepare_created_by(self, obj):
        return obj.created_by.full_name if obj.created_by else None

    def prepare_status(self, obj):
        return obj.status.name if obj.status else None

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def prepare_type(self, obj):
        return obj.type.name if obj.type else None

    class Meta:
        model = Case
                'profile_picture': obj.created_by.profile_picture,
