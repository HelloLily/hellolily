from django_elasticsearch_dsl import DocType, Index, IntegerField, TextField

from lily.tags.models import Tag
from lily.users.models import LilyUser
from lily.utils.models.models import EmailAddress, PhoneNumber
from .models import Account, AccountStatus, Website

index = Index('account')


@index.doc_type
class AccountDoc(DocType):
    assigned_to = TextField(related_model=LilyUser)
    description = TextField()
    email_addresses = TextField(related_model=EmailAddress)
    name = TextField()
    phone_numbers = TextField(related_model=PhoneNumber)
    status = TextField(related_model=AccountStatus)
    tags = TextField(related_model=Tag)
    tenant_id = IntegerField()
    websites = TextField(related_model=Website)

    def prepare_assigned_to(self, obj):
        return obj.assigned_to.full_name if obj.assigned_to else None

    def prepare_email_addresses(self, obj):
        return [email.email_address for email in obj.email_addresses.all()]

    def prepare_phone_numbers(self, obj):
        return [phone_number.number for phone_number in obj.phone_numbers.all()]

    def prepare_status(self, obj):
        return obj.status.name if obj.status else None

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def prepare_websites(self, obj):
        return [website.website for website in obj.websites.all()]

    def get_instances_from_assigned_to(self, user):
        return user.account_set.all()

    def get_instances_from_email_addresses(self, email_address):
        return email_address.account_set.all()

    def get_instances_from_phone_numbers(self, phone_number):
        return phone_number.account_set.all()

    def get_instances_from_status(self, status):
        return status.accounts.all()

    def get_instances_from_tags(self, tag):
        if tag.content_type.model == 'account':
            return Account.objects.get(pk=tag.object_id)

    def get_instances_from_websites(self, website):
        return website.account

    class Meta:
        model = Account
