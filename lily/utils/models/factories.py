import random

from factory.declarations import LazyAttribute
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice
from faker.factory import Factory

from .models import EmailAddress, PhoneNumber, Address, COUNTRIES, PHONE_TYPE_CHOICES

faker = Factory.create('nl_NL')


class PhoneNumberFactory(DjangoModelFactory):
    raw_input = LazyAttribute(lambda o: faker.phone_number())
    type = FuzzyChoice(dict(PHONE_TYPE_CHOICES).keys())

    class Meta:
        model = PhoneNumber


class AddressFactory(DjangoModelFactory):
    street = LazyAttribute(lambda o: faker.street_name())
    street_number = LazyAttribute(lambda o: faker.building_number())

    complement = LazyAttribute(lambda o: 'a' if random.randint(0, 100) < 40 else None)  # 40% chance of complement
    postal_code = LazyAttribute(lambda o: faker.postcode())
    city = LazyAttribute(lambda o: faker.city())
    state_province = LazyAttribute(lambda o: faker.province())
    country = FuzzyChoice(dict(COUNTRIES).keys())
    type = FuzzyChoice(dict(Address.ADDRESS_TYPE_CHOICES).keys())

    class Meta:
        model = Address


class EmailAddressFactory(DjangoModelFactory):
    email_address = LazyAttribute(lambda o: faker.safe_email())
    status = EmailAddress.PRIMARY_STATUS

    class Meta:
        model = EmailAddress


