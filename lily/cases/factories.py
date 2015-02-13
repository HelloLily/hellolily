import datetime

from factory.declarations import (SubFactory, LazyAttribute, SelfAttribute,
                                  Sequence, Iterator)
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from faker.factory import Factory

from lily.accounts.factories import AccountFactory
from lily.tenant.factories import TenantFactory
from lily.users.factories import LilyUserFactory

from .models import Case, CaseStatus, CaseType

faker = Factory.create()


class CaseTypeFactory(DjangoModelFactory):
    type = Iterator(['Order', 'Aftersales', 'Various'])

    class Meta:
        model = CaseType


class CaseStatusFactory(DjangoModelFactory):
    position = Sequence(int)
    status = LazyAttribute(lambda o: faker.word())

    class Meta:
        model = CaseStatus


class CaseFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    status = SubFactory(CaseStatusFactory, tenant=SelfAttribute('..tenant'))
    priority = FuzzyChoice(dict(Case.PRIORITY_CHOICES).keys())
    subject = LazyAttribute(lambda o: faker.word())
    account = SubFactory(AccountFactory, tenant=SelfAttribute('..tenant'))
    expires = FuzzyDate(datetime.date(2015, 1, 1), datetime.date(2016, 1, 1))
    assigned_to = SubFactory(LilyUserFactory, tenant=SelfAttribute('..tenant'))
    type = SubFactory(CaseTypeFactory, tenant=SelfAttribute('..tenant'))

    class Meta:
        model = Case
