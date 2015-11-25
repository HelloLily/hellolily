from factory.declarations import SubFactory, LazyAttribute, SelfAttribute
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDecimal, FuzzyChoice
from faker.factory import Factory

from lily.accounts.factories import AccountFactory
from lily.users.factories import LilyUserFactory
from lily.tenant.factories import TenantFactory

from .models import Deal


faker = Factory.create('nl_NL')


class DealFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    name = LazyAttribute(lambda o: faker.word())
    account = SubFactory(AccountFactory, tenant=SelfAttribute('..tenant'))
    amount_once = FuzzyDecimal(42.7)
    amount_recurring = FuzzyDecimal(42.7)
    assigned_to = SubFactory(LilyUserFactory, tenant=SelfAttribute('..tenant'))
    stage = FuzzyChoice(dict(Deal.STAGE_CHOICES).keys())

    class Meta:
        model = Deal
