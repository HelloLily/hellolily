from django_elasticsearch_dsl import DocType, Index, IntegerField

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.tags.models import Tag
from lily.users.models import LilyUser
from lily.search.fields import CharField
from .models import Case, CaseStatus, CaseType

index = Index('case')


@index.doc_type
class CaseDoc(DocType):
    account = CharField(related_model=Account)
    assigned_to = CharField(related_model=LilyUser)
    contact = CharField(related_model=Contact)
    created_by = CharField(related_model=LilyUser)
    status = CharField(related_model=CaseStatus)
    subject = CharField()
    tags = CharField(related_model=Tag)
    tenant_id = IntegerField()
    type = CharField(related_model=CaseType)

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

    def get_instances_from_account(self, account):
        return account.case_set.all()

    def get_instances_from_assigned_to(self, lily_user):
        return lily_user.assigned_cases.all()

    def get_instances_from_contact(self, contact):
        return contact.case_set.all()

    def get_instances_from_created_by(self, lily_user):
        return lily_user.created_cases.all()

    def get_instances_from_status(self, status):
        return status.cases.all()

    def get_instances_from_tags(self, tag):
        if tag.content_type.model == 'case':
            return Contact.objects.get(pk=tag.object_id)

    def get_instances_from_type(self, type):
        return type.cases.all()

    class Meta:
        model = Case
                'profile_picture': obj.created_by.profile_picture,
