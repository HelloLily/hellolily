from datetime import timedelta

import requests
from django.utils import timezone
from oauth2client.client import Credentials
from oauth2client.contrib.django_orm import Storage

from .models import IntegrationCredentials, IntegrationDetails


def get_credentials(integration_type):
    """
    Get the credentials for the given integration type.

    Arguments:
        tenant (instance): Tenant instance.
        type (integer): Type of the integration.

    Returns:
        Credentials for the given type.
    """
    details = IntegrationDetails.objects.get(type=integration_type)

    storage = Storage(IntegrationCredentials, 'details', details, 'credentials')
    credentials = storage.get()

    if credentials.expires and timezone.now() > credentials.expires:
        # Credentials have expired, so refresh the token.
        credentials = authenticate_pandadoc(credentials, integration_type)

    return credentials


def authenticate_pandadoc(credentials, integration_type, code=None):
    payload = {
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
    }

    if code:
        # Trade the auth code for an access token.
        payload.update({
            'grant_type': 'authorization_code',
            'code': code
        })
    else:
        # Already authenticated once, but access token expired.
        payload.update({
            'grant_type': 'refresh_token',
            'refresh_token': credentials.refresh_token
        })

    response = requests.post(
        url='https://api.pandadoc.com/oauth2/access_token',
        data=payload,
    )

    if response.status_code == 200:
        data = response.json()

        credentials.access_token = data.get('access_token')
        credentials.refresh_token = data.get('refresh_token')
        credentials.expires = timezone.now() + timedelta(seconds=data.get('expires_in'))

        details = IntegrationDetails.objects.get(type=integration_type)
        storage = Storage(IntegrationCredentials, 'details', details, 'credentials')

        storage.put(credentials)

        return credentials


class LilyOAuthCredentials(Credentials):
    def __init__(self, client_id, client_secret, access_token=None, refresh_token=None, expires=None):
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.expires = expires
