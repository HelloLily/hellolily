from factory import post_generation
from factory.declarations import (LazyAttribute, SubFactory, RelatedFactory, SelfAttribute)
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice
from faker.factory import Factory

from lily.accounts.factories import AccountFactory
from lily.tenant.factories import TenantFactory
from lily.utils.models.factories import EmailAddressFactory

from .models import Contact, Function

faker = Factory.create('nl_NL')


class ContactFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    first_name = LazyAttribute(lambda o: faker.first_name())
    last_name = LazyAttribute(lambda o: faker.last_name())
    gender = FuzzyChoice(dict(Contact.CONTACT_GENDER_CHOICES).keys())
    title = LazyAttribute(lambda o: faker.word())
    description = LazyAttribute(lambda o: faker.text())
    salutation = FuzzyChoice(dict(Contact.SALUTATION_CHOICES).keys())

    class Meta:
        model = Contact


class ContactWithEmailFactory(ContactFactory):
    @post_generation
    def email_addresses(self, create, extracted, **kwargs):
        if create:
            email_str = '%s.%s@%s' % (self.first_name.lower(), self.last_name.lower(), faker.free_email_domain())

            email_address = EmailAddressFactory(tenant=self.tenant, email_address=email_str)
            self.email_addresses.add(email_address)


class FunctionFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    contact = SubFactory(ContactFactory, tenant=SelfAttribute('..tenant'))
    account = SubFactory(AccountFactory, tenant=SelfAttribute('..tenant'))

    class Meta:
        model = Function
        exclude = ('tenant', )  # Tenant is a field because of the relations, but not because a function has a tenant.


class ContactWithAccountFactory(ContactWithEmailFactory):
    function = RelatedFactory(FunctionFactory, 'contact')
