import datetime

from factory import post_generation
from factory.declarations import SubFactory, LazyAttribute, SelfAttribute, Iterator, Sequence
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDecimal, FuzzyChoice, FuzzyDate
from faker.factory import Factory

from lily.accounts.factories import AccountFactory
from lily.users.factories import LilyUserFactory
from lily.tenant.factories import TenantFactory

from .models import Deal, DealNextStep, DealWhyCustomer, DealWhyLost, DealFoundThrough, DealContactedBy, DealStatus

faker = Factory.create('nl_NL')
past_date = datetime.date.today() - datetime.timedelta(days=10)
future_date = datetime.date.today() + datetime.timedelta(days=10)

NEXT_STEP_NAMES = [
    'Follow up',
    'Activation',
    'Request feedback',
    'None'
]

NEXT_STEP_DATE_INCREMENTS = [4, 2, 30, 0]


class DealNextStepFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    name = Iterator(NEXT_STEP_NAMES)
    date_increment = Iterator(NEXT_STEP_DATE_INCREMENTS)

    class Meta:
        model = DealNextStep
        django_get_or_create = ('tenant', 'name', 'date_increment')


class DealWhyCustomerFactory(DjangoModelFactory):
    name = LazyAttribute(lambda o: faker.word())

    class Meta:
        model = DealWhyCustomer


class DealWhyLostFactory(DjangoModelFactory):
    position = Sequence(int)
    name = LazyAttribute(lambda o: faker.word())
    tenant = SubFactory(TenantFactory)

    class Meta:
        model = DealWhyLost
        django_get_or_create = ('tenant', 'name')


FOUND_THROUGH_NAMES = [
    'Search engine',
    'Social media',
    'Talk with employee',
    'Existing customer',
    'Other',
    'Radio',
    'Public speaking',
    'Press and articles',
]


class DealFoundThroughFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    name = Iterator(FOUND_THROUGH_NAMES)

    class Meta:
        model = DealFoundThrough
        django_get_or_create = ('tenant', 'name')


CONTACTED_BY_NAMES = [
    'Quote',
    'Contact form',
    'Phone',
    'Web chat',
    'E-mail',
    'Instant connect',
    'Other',
]


class DealContactedByFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    name = Iterator(CONTACTED_BY_NAMES)

    class Meta:
        model = DealContactedBy
        django_get_or_create = ('tenant', 'name')


STATUS_NAMES = [
    'Open',
    'Proposal sent',
    'Won',
    'Lost',
    'Called',
    'Emailed',
]


class DealStatusFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    name = Iterator(STATUS_NAMES)

    class Meta:
        model = DealStatus
        django_get_or_create = ('tenant', 'name')


class DealFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    account = SubFactory(AccountFactory, tenant=SelfAttribute('..tenant'))
    amount_once = FuzzyDecimal(42.7)
    amount_recurring = FuzzyDecimal(42.7)
    assigned_to = SubFactory(LilyUserFactory, tenant=SelfAttribute('..tenant'))
    card_sent = FuzzyChoice([True, False])
    contacted_by = SubFactory(DealContactedByFactory, tenant=SelfAttribute('..tenant'))
    currency = FuzzyChoice(dict(Deal.CURRENCY_CHOICES).keys())
    feedback_form_sent = FuzzyChoice([True, False])
    found_through = SubFactory(DealFoundThroughFactory, tenant=SelfAttribute('..tenant'))
    is_checked = FuzzyChoice([True, False])
    name = LazyAttribute(lambda o: faker.word())
    new_business = FuzzyChoice([True, False])
    next_step = SubFactory(DealNextStepFactory, tenant=SelfAttribute('..tenant'))
    next_step_date = FuzzyDate(past_date, future_date)
    status = SubFactory(DealStatusFactory, tenant=SelfAttribute('..tenant'))
    twitter_checked = FuzzyChoice([True, False])
    why_customer = SubFactory(DealWhyCustomerFactory, tenant=SelfAttribute('..tenant'))
    why_lost = None

    @post_generation
    def why_lost(self, create, extracted, **kwargs):
        # If a deal was created with the 'Lost' status we want to set a lost reason.
        if self.status.name == 'Lost':
            self.why_lost = DealWhyLostFactory(tenant=self.tenant)

    class Meta:
        model = Deal
