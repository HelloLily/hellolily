from django_elasticsearch_dsl import DocType, Index, IntegerField, ObjectField, TextField

from .models import Contact

index = Index('contact')


@index.doc_type
class ContactDoc(DocType):
    accounts = ObjectField(properties={
        'id': IntegerField(),
        'name': TextField(),
        'phone_numbers': TextField(),
    })
    description = TextField()
    email_address = TextField()
    full_name = TextField()
    phone_numbers = TextField()
    tags = TextField()
    tenant_id = IntegerField()

    def _convert_function_to_account(self, func):
        return {
            'id': func.account_id,
            'name': func.account.name if func.account.name else '',
            'phone_numbers': [phone_number.number for phone_number in func.account.phone_numbers.all()],
        }

    def prepare_accounts(self, obj):
        functions = obj.functions.filter(account__is_deleted=False)

        return [self._convert_function_to_account(func) for func in functions]

    def prepare_email_address(self, obj):
        return [email.email_address for email in obj.email_addresses.all()]

    def prepare_phone_numbers(self, obj):
        return [phone_number.number for phone_number in obj.phone_numbers.all()]

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    class Meta:
        model = Contact
