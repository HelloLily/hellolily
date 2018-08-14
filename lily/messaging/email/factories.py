import datetime
import unicodedata

from django.utils.timezone import utc
from factory.declarations import SubFactory, LazyAttribute
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyText, FuzzyInteger
from faker.factory import Factory
from factory.helpers import post_generation

from lily.tenant.factories import TenantFactory
from lily.users.factories import LilyUserFactory
from .models.models import EmailAccount, EmailMessage, Recipient, EmailLabel

faker = Factory.create('nl_NL')

current_date = datetime.datetime.now()
past_date = current_date - datetime.timedelta(days=10)


class EmailAccountFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    owner = SubFactory(LilyUserFactory)
    email_address = LazyAttribute(lambda o: unicodedata.normalize('NFD', faker.safe_email()).encode('ascii', 'ignore'))
    from_name = LazyAttribute(lambda o: faker.name())
    label = LazyAttribute(lambda o: faker.word())
    is_authorized = True
    privacy = FuzzyChoice(dict(EmailAccount.PRIVACY_CHOICES).keys())

    class Meta:
        model = EmailAccount


class RecipientFactory(DjangoModelFactory):
    name = LazyAttribute(lambda o: faker.name())
    email_address = LazyAttribute(lambda o: unicodedata.normalize('NFD', faker.safe_email()).encode('ascii', 'ignore'))

    class Meta:
        model = Recipient


class EmailMessageFactory(DjangoModelFactory):
    subject = LazyAttribute(lambda o: faker.word())
    sender = SubFactory(RecipientFactory)
    body_text = LazyAttribute(lambda o: faker.text())
    sent_date = LazyAttribute(lambda o: faker.date_time_between_dates(past_date, current_date, utc))
    account = SubFactory(EmailAccountFactory)
    message_id = FuzzyText()

    @post_generation
    def received_by(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            if isinstance(extracted, Recipient):
                # A single team was passed in, use that.
                self.received_by.add(extracted)
            else:
                # A list of teams were passed in, use them.
                for recipient in extracted:
                    self.received_by.add(recipient)

    class Meta:
        model = EmailMessage


class EmailLabelFactory(DjangoModelFactory):
    account = SubFactory(EmailAccountFactory)
    label_type = FuzzyChoice(dict(EmailLabel.LABEL_TYPES).keys())
    label_id = FuzzyText()
    name = label_id
    unread = FuzzyInteger(0, 42)

    class Meta:
        model = EmailLabel
