import unicodedata
from factory.declarations import LazyAttribute
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice
from faker.factory import Factory

from .models import EmailAddress, PhoneNumber, Address, PHONE_TYPE_CHOICES, ExternalAppLink, Webhook
from lily.utils.countries import COUNTRIES

faker = Factory.create('nl_NL')


class PhoneNumberFactory(DjangoModelFactory):
    number = LazyAttribute(lambda o: faker.phone_number())
    type = FuzzyChoice(dict(PHONE_TYPE_CHOICES).keys())

    class Meta:
        model = PhoneNumber


class AddressFactory(DjangoModelFactory):
    address = LazyAttribute(lambda o: faker.street_address())
    postal_code = LazyAttribute(lambda o: faker.postcode())
    city = LazyAttribute(lambda o: faker.city())
    state_province = LazyAttribute(lambda o: faker.province())
    country = FuzzyChoice(dict(COUNTRIES).keys())
    type = FuzzyChoice(dict(Address.ADDRESS_TYPE_CHOICES).keys())

    class Meta:
        model = Address


class EmailAddressFactory(DjangoModelFactory):
    email_address = LazyAttribute(lambda o: unicodedata.normalize('NFD', faker.safe_email()).encode('ascii', 'ignore'))
    status = EmailAddress.PRIMARY_STATUS

    class Meta:
        model = EmailAddress


class ExternalAppLinkFactory(DjangoModelFactory):
    name = LazyAttribute(lambda o: faker.company())
    url = LazyAttribute(lambda o: faker.url())

    class Meta:
        model = ExternalAppLink


class WebhookFactory(DjangoModelFactory):
    name = LazyAttribute(lambda o: faker.company())
    url = LazyAttribute(lambda o: faker.url())

    class Meta:
        model = Webhook
