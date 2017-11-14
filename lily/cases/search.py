from django_elasticsearch_dsl import DocType, Index, IntegerField

from lily.search.fields import CharField
from .models import Case

index = Index('case')


@index.doc_type
class CaseDoc(DocType):
    account = CharField()
    assigned_to = CharField()
    contact = CharField()
    created_by = CharField()
    status = CharField()
    subject = CharField()
    tags = CharField()
    tenant_id = IntegerField()
    type = CharField()

    def get_queryset(self):
        return Case.objects.select_related(
            'assigned_to', 'contact', 'created_by', 'status', 'type',
        ).prefetch_related('tags')

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
