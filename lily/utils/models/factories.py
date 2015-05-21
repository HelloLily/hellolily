from factory.django import DjangoModelFactory
from faker.factory import Factory

from .models import EmailAddress, PhoneNumber


faker = Factory.create()


class EmailAddressFactory(DjangoModelFactory):
    status = EmailAddress.PRIMARY_STATUS

    class Meta:
        model = EmailAddress


class PhoneNumberFactory(DjangoModelFactory):
    number = faker.phone_number()

    class Meta:
        model = PhoneNumber
