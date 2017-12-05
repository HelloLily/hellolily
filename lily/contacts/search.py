from django_elasticsearch_dsl import DocType, Index, IntegerField, ObjectField

from lily.search.fields import CharField, EmailAddressField, PhoneNumberField
from lily.accounts.models import Account
from lily.tags.models import Tag
from lily.utils.models.models import PhoneNumber, EmailAddress
from .models import Contact

index = Index('contact')


@index.doc_type
class ContactDoc(DocType):
    accounts = ObjectField(properties={
        'id': IntegerField(),
        'name': CharField(),
        'phone_numbers': PhoneNumberField(related_model=PhoneNumber),
    }, related_model=Account)
    description = CharField()
    email_address = EmailAddressField(related_model=EmailAddress)
    full_name = CharField()
    phone_numbers = PhoneNumberField(related_model=PhoneNumber)
    tags = CharField(related_model=Tag)
    tenant_id = IntegerField()

    def get_queryset(self):
        return Contact.objects.prefetch_related('email_addresses', 'phone_numbers', 'tags')

    def prepare_accounts(self, obj):
        functions = obj.functions.filter(
            account__is_deleted=False
        ).select_related('account').prefetch_related('account__phone_numbers')

        return [self._convert_function_to_account(func) for func in functions]

    def _convert_function_to_account(self, func):
        return {
            'id': func.account_id,
            'name': func.account.name if func.account.name else '',
            'phone_numbers': [phone_number.number for phone_number in func.account.phone_numbers.all()],
        }

    def prepare_email_address(self, obj):
        return [email.email_address for email in obj.email_addresses.all()]

    def prepare_phone_numbers(self, obj):
        return [phone_number.number for phone_number in obj.phone_numbers.all()]

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def get_instances_from_accounts(self, account):
        return account.contacts.all()

    def get_instances_from_accounts_phone_numbers(self, phone_number):
        return Contact.objects.filter(accounts__phone_numbers=phone_number)

    def get_instances_from_email_addresses(self, email_address):
        return email_address.contact_set.all()

    def get_instances_from_phone_numbers(self, phone_number):
        return phone_number.contact_set.all()

    def get_instances_from_tags(self, tag):
        if tag.content_type.model == 'contact':
            return Contact.objects.get(pk=tag.object_id)

    class Meta:
        model = Contact
