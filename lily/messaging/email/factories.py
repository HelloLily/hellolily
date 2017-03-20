import factory
import unicodedata

from factory.declarations import LazyAttribute
from faker.factory import Factory
from .models.models import EmailAccount, EmailMessage, EmailHeader, EmailLabel

faker = Factory.create('nl_NL')


class GmailAccountFactory(factory.DjangoModelFactory):
    email_address = LazyAttribute(lambda o: unicodedata.normalize('NFD', faker.safe_email()).encode('ascii', 'ignore'))
    from_name = LazyAttribute(lambda o: faker.first_name().lower())
    label = from_name
    is_authorized = True

    class Meta:
        model = EmailAccount


class GmailMessageFactory(factory.DjangoModelFactory):
    account = factory.SubFactory(GmailAccountFactory)

    class Meta:
        model = EmailMessage


class GmailHeaderFactory(factory.DjangoModelFactory):
    message = factory.SubFactory(GmailMessageFactory)

    class Meta:
        model = EmailHeader


class GmailLabelFactory(factory.DjangoModelFactory):
    label_id = factory.Sequence(lambda n: 'Label_{0}'.format(n))

    class Meta:
        model = EmailLabel
