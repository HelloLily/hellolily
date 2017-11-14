from django_elasticsearch_dsl import DocType, Index, IntegerField

from lily.search.fields import CharField
from .models import Deal

index = Index('deal')


@index.doc_type
class DealDoc(DocType):
    account = CharField()
    assigned_to = CharField()
    created_by = CharField()
    contact = CharField()
    contacted_by = CharField()
    name = CharField()
    status = CharField()
    tags = CharField()
    tenant_id = IntegerField()

    def get_queryset(self):
        return Deal.objects.select_related(
            'account', 'assigned_to', 'created_by', 'contact', 'contacted_by', 'status',
        ).prefetch_related('tags')

    def prepare_account(self, obj):
        return obj.account.name if obj.account else None

    def prepare_assigned_to(self, obj):
        return obj.assigned_to.full_name if obj.assigned_to else None

    def prepare_created_by(self, obj):
        return obj.created_by.full_name if obj.created_by else None

    def prepare_contact(self, obj):
        return obj.contact.full_name if obj.contact else None

    def prepare_contacted_by(self, obj):
        return obj.contacted_by.name if obj.contacted_by else None

    def prepare_status(self, obj):
        return obj.status.name if obj.status else None

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    class Meta:
        model = Deal
                'profile_picture': obj.assigned_to.profile_picture,
                'profile_picture': obj.created_by.profile_picture,
