from factory.declarations import LazyAttribute
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyInteger, FuzzyText
from faker.factory import Factory

from .models import Call

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
