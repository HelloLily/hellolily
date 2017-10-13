from factory.declarations import LazyAttribute, SubFactory, SelfAttribute
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyInteger, FuzzyText
from faker.factory import Factory
from pytz import UTC

from lily.tenant.factories import TenantFactory
from .models import Call, CallRecord, CallParticipant, CallTransfer

faker = Factory.create('nl_NL')


class CallFactory(DjangoModelFactory):
    unique_id = FuzzyText()
    called_number = LazyAttribute(lambda o: faker.phone_number())
    caller_number = LazyAttribute(lambda o: faker.phone_number())
    internal_number = FuzzyInteger(200, 999)
    status = FuzzyChoice(dict(Call.CALL_STATUS_CHOICES).keys())
    type = FuzzyChoice(dict(Call.CALL_TYPE_CHOICES).keys())

    class Meta:
        model = Call


class CallParticipantFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    number = LazyAttribute(lambda o: faker.phone_number())
    name = LazyAttribute(lambda o: faker.name())

    class Meta:
        model = CallParticipant


class CallRecordFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    call_id = FuzzyText(length=40)
    start = LazyAttribute(lambda o: faker.date_time(tzinfo=UTC))
    end = LazyAttribute(lambda o: faker.date_time_between(start_date="now", end_date="+15m", tzinfo=UTC))
    status = FuzzyChoice(dict(CallRecord.CALL_STATUS_CHOICES).keys())
    direction = FuzzyChoice(dict(CallRecord.CALL_DIRECTION_CHOICES).keys())
    caller = SubFactory(CallParticipantFactory, tenant=SelfAttribute('..tenant'))
    destination = SubFactory(CallParticipantFactory, tenant=SelfAttribute('..tenant'))

    class Meta:
        model = CallRecord


class CallTransferFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    timestamp = LazyAttribute(lambda o: faker.date_time_between(start_date="now", end_date="+1m", tzinfo=UTC))
    destination = SubFactory(CallParticipantFactory, tenant=SelfAttribute('..tenant'))

    class Meta:
        model = CallTransfer
