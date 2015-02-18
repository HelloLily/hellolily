import factory

from lily.users.factories import LilyUserFactory

from .models.models import EmailAccount, EmailMessage, EmailHeader, EmailLabel


class GmailAccountFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(LilyUserFactory)

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
