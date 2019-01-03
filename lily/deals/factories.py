import datetime
from django.utils.timezone import utc

from factory.declarations import SubFactory, LazyAttribute, SelfAttribute, Iterator, Sequence
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from faker.factory import Factory

from lily.accounts.factories import AccountFactory
from lily.contacts.factories import ContactFactory
from lily.users.factories import LilyUserFactory
from lily.utils.currencies import CURRENCIES
from lily.tenant.factories import TenantFactory

from .models import Deal, DealNextStep, DealWhyCustomer, DealWhyLost, DealFoundThrough, DealContactedBy, DealStatus

faker = Factory.create('nl_NL')
past_date = datetime.date.today() - datetime.timedelta(days=10)
future_date = datetime.date.today() + datetime.timedelta(days=10)
current_date = datetime.date.today()

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
    'Email',
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
    contact = SubFactory(ContactFactory, tenant=SelfAttribute('..tenant'))
    # Quick fix: FuzzyDecimal (what amount_* was before) is not correctly serialized in some cases, cannot seem to find
    # what causes it. For now I'll do it like this, this is a reminder to myself to work on it later. (before this is
    # merged)
    # amount_once = FuzzyDecimal(42.7)
    # amount_recurring = FuzzyDecimal(42.7)
    amount_once = 42.7
    amount_recurring = 42.7
    assigned_to = SubFactory(LilyUserFactory, tenant=SelfAttribute('..tenant'))
    card_sent = FuzzyChoice([True, False])
    contacted_by = SubFactory(DealContactedByFactory, tenant=SelfAttribute('..tenant'))
    currency = FuzzyChoice(dict(CURRENCIES).keys())
    found_through = SubFactory(DealFoundThroughFactory, tenant=SelfAttribute('..tenant'))
    is_checked = FuzzyChoice([True, False])
    name = LazyAttribute(lambda o: faker.word())
    new_business = FuzzyChoice([True, False])
    next_step = SubFactory(DealNextStepFactory, tenant=SelfAttribute('..tenant'))
    next_step_date = FuzzyDate(past_date, future_date)
    status = SubFactory(DealStatusFactory, tenant=SelfAttribute('..tenant'))
    twitter_checked = FuzzyChoice([True, False])
    why_customer = SubFactory(DealWhyCustomerFactory, tenant=SelfAttribute('..tenant'))
    why_lost = SubFactory(DealWhyLostFactory,
                          tenant=SelfAttribute('..tenant'),
                          name=LazyAttribute(lambda o: faker.word() if o.factory_parent.status.is_lost else "")
                          )
    closed_date = LazyAttribute(
        lambda o: faker.date_time_between_dates(
            past_date, current_date, utc
        ) if o.status.is_won or o.status.is_lost else None
    )

    class Meta:
        model = Deal
