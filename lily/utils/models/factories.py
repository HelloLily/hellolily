from factory.django import DjangoModelFactory
from faker.factory import Factory

from lily.utils.models.models import EmailAddress, PhoneNumber


faker = Factory.create()


class EmailAddressFactory(DjangoModelFactory):
    is_primary = True

    class Meta:
        model = EmailAddress


class PhoneNumberFactory(DjangoModelFactory):
    number = faker.phone_number()

    class Meta:
        model = PhoneNumber
