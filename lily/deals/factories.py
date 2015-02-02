import datetime

from factory.declarations import SubFactory, LazyAttribute, SelfAttribute
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDecimal, FuzzyDate, FuzzyChoice
from faker.factory import Factory

from lily.accounts.factories import AccountFactory
from lily.deals.models import Deal
from lily.users.factories import LilyUserFactory


faker = Factory.create()


class DealFactory(DjangoModelFactory):
    name = LazyAttribute(lambda o: faker.word())
    account = SubFactory(AccountFactory, tenant=SelfAttribute('..tenant'))
    amount_once = FuzzyDecimal(42.7)
    amount_recurring = FuzzyDecimal(42.7)
    expected_closing_date = FuzzyDate(datetime.date(2015, 1, 1), datetime.date(2016, 1, 1))
    assigned_to = SubFactory(LilyUserFactory, tenant=SelfAttribute('..tenant'))
    stage = FuzzyChoice(dict(Deal.STAGE_CHOICES).keys())

    class Meta:
        model = Deal
