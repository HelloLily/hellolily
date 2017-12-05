from django_elasticsearch_dsl import DocType, Index, IntegerField, TextField

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.tags.models import Tag
from lily.users.models import LilyUser
from .models import Case, CaseStatus, CaseType

index = Index('case')


@index.doc_type
class CaseDoc(DocType):
    account = TextField(related_model=Account)
    assigned_to = TextField(related_model=LilyUser)
    contact = TextField(related_model=Contact)
    created_by = TextField(related_model=LilyUser)
    status = TextField(related_model=CaseStatus)
    subject = TextField()
    tags = TextField(related_model=Tag)
    tenant_id = IntegerField()
    type = TextField(related_model=CaseType)

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
