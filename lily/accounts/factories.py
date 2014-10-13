import factory
from factory.declarations import LazyAttribute
from factory.django import DjangoModelFactory
from faker.factory import Factory

from lily.accounts.models import Account
from lily.utils.models.factories import PhoneNumberFactory


faker = Factory.create()


class AccountFactory(DjangoModelFactory):
    name = LazyAttribute(lambda o: faker.company())
    description = LazyAttribute(lambda o: faker.bs())

    @factory.post_generation
    def phone_numbers(self, create, extracted, **kwargs):
        phone_str = faker.phone_number()

        phone_number = PhoneNumberFactory(tenant=self.tenant, raw_input=phone_str)
        self.phone_numbers.add(phone_number)

    class Meta:
        model = Account
