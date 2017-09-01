from django_elasticsearch_dsl import DocType, Index, IntegerField, TextField

from .models import Account

index = Index('account')


@index.doc_type
class AccountDoc(DocType):
    assigned_to = TextField()
    description = TextField()
    email_addresses = TextField()
    name = TextField()
    phone_numbers = TextField()
    status = TextField()
    tags = TextField()
    tenant_id = IntegerField()
    websites = TextField()

    def prepare_assigned_to(self, obj):
        return obj.assigned_to.full_name if obj.assigned_to else None

    def prepare_contacts(self, obj):
        return [contact.id for contact in obj.contacts.all()]

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

    class Meta:
        model = Account
