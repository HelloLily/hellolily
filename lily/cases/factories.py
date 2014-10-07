import datetime

from factory.declarations import SubFactory, LazyAttribute, SelfAttribute
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from faker.factory import Factory

from lily.accounts.factories import AccountFactory
from lily.cases.models import Case
from lily.users.factories import CustomUserFactory


faker = Factory.create()


class CaseFactory(DjangoModelFactory):
    class Meta:
        model = Case

    status = FuzzyChoice(dict(Case.STATUS_CHOICES).keys())
    priority = FuzzyChoice(dict(Case.PRIORITY_CHOICES).keys())
    subject = LazyAttribute(lambda o: faker.word())
    account = SubFactory(AccountFactory, tenant=SelfAttribute('..tenant'))
    expires = FuzzyDate(datetime.date(2015, 1, 1), datetime.date(2016, 1, 1))
    assigned_to = SubFactory(CustomUserFactory, tenant=SelfAttribute('..tenant'))
