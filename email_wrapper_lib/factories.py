from datetime import datetime
from factory.declarations import LazyAttribute, Iterator, SelfAttribute
from factory.django import DjangoModelFactory
from faker.factory import Factory
from oauth2client.client import OAuth2Credentials

from .models import EmailAccount

faker = Factory.create('nl_NL')


def generate_credentials():
    return OAuth2Credentials(
        access_token=faker.ean(length=13),
        client_id='client_id',
        client_secret='client_secret',
        refresh_token='refresh_token',
        token_expiry=datetime(year=2020, month=7, day=7),
        token_uri='token_uri',
        user_agent=None,
        revoke_uri='revoke_uri',
        id_token='extracted_id_token',
        token_response='token_response',
        scopes='mail.fake.com',
        token_info_uri='token_info_uri'
    )


class EmailAccountFactory(DjangoModelFactory):
    username = LazyAttribute(lambda o: faker.safe_email())
    user_id = SelfAttribute('.username')
    credentials = LazyAttribute(lambda o: generate_credentials())
    status = Iterator(range(5))
    provider_id = Iterator(range(1, 3))

    class Meta:
        model = EmailAccount
