import factory
from factory.declarations import LazyAttribute
from factory.django import DjangoModelFactory
from faker.factory import Factory

from lily.tenant.factories import TenantFactory
from lily.utils.models.factories import PhoneNumberFactory

from .models import Account

faker = Factory.create('nl_NL')


class AccountFactory(DjangoModelFactory):
    tenant = factory.SubFactory(TenantFactory)
    name = LazyAttribute(lambda o: faker.company())
    description = LazyAttribute(lambda o: faker.bs())

    @factory.post_generation
    def phone_numbers(self, create, extracted, **kwargs):
        phone_str = faker.phone_number()
        if create:
            phone_number = PhoneNumberFactory(tenant=self.tenant, raw_input=phone_str)
            self.phone_numbers.add(phone_number)

    class Meta:
        model = Account
