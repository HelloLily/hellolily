from django_elasticsearch_dsl import DocType, Index, IntegerField

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.tags.models import Tag
from lily.users.models import LilyUser
from lily.search.fields import CharField
from .models import Deal, DealStatus, DealContactedBy


index = Index('deal')


@index.doc_type
class DealDoc(DocType):
    account = CharField(related_model=Account)
    assigned_to = CharField(related_model=LilyUser)
    created_by = CharField(related_model=LilyUser)
    contact = CharField(related_model=Contact)
    contacted_by = CharField(related_model=DealContactedBy)
    name = CharField()
    status = CharField(related_model=DealStatus)
    tags = CharField(related_model=Tag)
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

    def get_instances_from_account(self, account):
        return account.deal_set.all()

    def get_instances_from_assigned_to(self, user):
        return user.deal_set.all()

    def get_instances_from_created_by(self, user):
        return user.created_deals.all()

    def get_instances_from_contact(self, contact):
        return contact.deal_set.all()

    def get_instances_from_contacted_by(self, contacted_by):
        return contacted_by.deals.all()

    def get_instances_from_status(self, status):
        return status.deals.all()

    def get_instances_from_tags(self, tag):
        if tag.content_type.model == 'deal':
            return Deal.objects.get(pk=tag.object_id)

    class Meta:
        model = Deal
