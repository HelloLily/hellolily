import datetime
import factory

from factory.declarations import (SubFactory, LazyAttribute, SelfAttribute, Sequence, Iterator)
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from faker.factory import Factory

from lily.accounts.factories import AccountFactory
from lily.tenant.factories import TenantFactory
from lily.users.factories import LilyUserFactory
from lily.users.models import Team

from .models import Case, CaseStatus, CaseType

faker = Factory.create('nl_NL')

CASESTATUS_CHOICES = (
    'New',
    'Closed',
    'Pending input',
    'Waiting on hardware',
    'Follow up',
    'Client will contact us',
    'Documentation',
)

CASETYPE_CHOICES = (
    'Config',
    'Support',
    'Return Shipment',
    'Callback',
    'Document',
    'Implement',
    'Misc',
    'Advice'
    'Customer Happiness',
)


class CaseTypeFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    name = Iterator(CASETYPE_CHOICES)

    class Meta:
        model = CaseType
        django_get_or_create = ('tenant', 'name')


class CaseStatusFactory(DjangoModelFactory):
    position = Sequence(int)
    name = Iterator(CASESTATUS_CHOICES)
    tenant = SubFactory(TenantFactory)

    class Meta:
        model = CaseStatus
        django_get_or_create = ('tenant', 'name')


class CaseFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    status = SubFactory(CaseStatusFactory, tenant=SelfAttribute('..tenant'))
    priority = FuzzyChoice(dict(Case.PRIORITY_CHOICES).keys())
    subject = LazyAttribute(lambda o: faker.word())
    account = SubFactory(AccountFactory, tenant=SelfAttribute('..tenant'))
    expires = FuzzyDate(datetime.date(2015, 1, 1), datetime.date(2016, 1, 1))
    assigned_to = SubFactory(LilyUserFactory, tenant=SelfAttribute('..tenant'))
    type = SubFactory(CaseTypeFactory, tenant=SelfAttribute('..tenant'))
    created_by = SelfAttribute('.assigned_to')

    @factory.post_generation
    def teams(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            if isinstance(extracted, Team):
                # A single team was passed in, use that.
                self.assigned_to_teams.add(extracted)
            else:
                # A list of teams were passed in, use them.
                for team in extracted:
                    self.assigned_to_teams.add(team)

    class Meta:
        model = Case
