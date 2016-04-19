import factory
from factory.declarations import LazyAttribute, SubFactory, Iterator, SelfAttribute
from factory.django import DjangoModelFactory
from faker.factory import Factory

from lily.tenant.factories import TenantFactory
from lily.utils.models.factories import PhoneNumberFactory

from .models import Account, AccountStatus

faker = Factory.create('nl_NL')

STATUS_NAMES = [
    'Previous customer',
    'Active',
    'Relation',
    'Prospect',
]


class AccountStatusFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    name = Iterator(STATUS_NAMES)

    class Meta:
        model = AccountStatus
        django_get_or_create = ('tenant', 'name')


class AccountFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    name = LazyAttribute(lambda o: faker.company())
    description = LazyAttribute(lambda o: faker.bs())
    status = SubFactory(AccountStatusFactory, tenant=SelfAttribute('..tenant'))

    @factory.post_generation
    def phone_numbers(self, create, extracted, **kwargs):
        phone_str = faker.phone_number()
        if create:
            phone_number = PhoneNumberFactory(tenant=self.tenant, number=phone_str)
            self.phone_numbers.add(phone_number)

    class Meta:
        model = Account
