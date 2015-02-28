import factory
from factory.declarations import (LazyAttribute, SubFactory, RelatedFactory, SelfAttribute)
from factory.django import DjangoModelFactory
from faker.factory import Factory

from lily.accounts.factories import AccountFactory
from lily.tenant.factories import TenantFactory
from lily.utils.models.factories import EmailAddressFactory

from .models import Contact, Function


faker = Factory.create()


class ContactFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    first_name = LazyAttribute(lambda o: faker.first_name())
    last_name = LazyAttribute(lambda o: faker.last_name())

    class Meta:
        model = Contact


class ContactWithEmailFactory(ContactFactory):
    @factory.post_generation
    def email_addresses(self, create, extracted, **kwargs):
        if create:
            email_str = '%s.%s@%s' % (
                self.first_name.lower(),
                self.last_name.lower(),
                faker.free_email_domain()
            )

            email_address = EmailAddressFactory(tenant=self.tenant, email_address=email_str)
            self.email_addresses.add(email_address)


def function_factory(tenant):
    # This factory is method wrapped, because Function itself does not accept tenant.
    # (Otherwise we could just pass the factory a tenant kwarg).
    class FunctionFactory(DjangoModelFactory):
        contact = SubFactory(ContactFactory, tenant=tenant)
        account = SubFactory(AccountFactory, tenant=tenant)

        class Meta:
            model = Function

    return FunctionFactory


class ContactWithAccountFactory(ContactWithEmailFactory):
    function = RelatedFactory(function_factory(SelfAttribute('..contact.tenant')), 'contact')
