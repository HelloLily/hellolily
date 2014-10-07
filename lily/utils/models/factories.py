from factory.django import DjangoModelFactory
from faker.factory import Factory

from lily.utils.models.models import EmailAddress, PhoneNumber


faker = Factory.create()


class EmailAddressFactory(DjangoModelFactory):
    class Meta:
        model = EmailAddress

    is_primary = True


class PhoneNumberFactory(DjangoModelFactory):
    class Meta:
        model = PhoneNumber

    number = faker.phone_number()
