import factory
from factory.declarations import LazyAttribute, SubFactory, Iterator, SelfAttribute
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice
from faker.factory import Factory

from lily.tenant.factories import TenantFactory
from lily.utils.models.factories import PhoneNumberFactory

from .models import Account, AccountStatus, Website

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

    @factory.post_generation
    def websites(self, create, extracted, **kwargs):

        if not create:
            return

        size = extracted.get('size', 1) if extracted else 1
        WebsiteFactory.create_batch(size=size, account=self, tenant=self.tenant)

    class Meta:
        model = Account


class WebsiteFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    account = SubFactory(AccountFactory, tenant=SelfAttribute('..tenant'))
    website = LazyAttribute(lambda o: faker.url())
    is_primary = FuzzyChoice([True, False])

    class Meta:
        model = Website
