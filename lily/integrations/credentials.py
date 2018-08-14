from datetime import timedelta

import requests
from django.utils import timezone
from oauth2client.client import Credentials
from oauth2client.contrib.django_orm import Storage

from .models import IntegrationCredentials, IntegrationDetails, SlackDetails, IntegrationType


def get_credentials(integration_type, tenant=None):
    """
    Get the credentials for the given integration type.

    Args:
        integration_type (str): Name of the integration for which the credentials should be retrieved.

    Returns:
        credentials (obj): Credentials for the given type.
    """
    try:
        integration_type = IntegrationType.objects.get(name__iexact=integration_type)
    except IntegrationType.DoesNotExist:
        details = None
    else:
        try:
            if tenant:
                # Calling from an 'anonymous' views (e.g. tasks). So add tenant filter.
                details = IntegrationDetails.objects.get(type=integration_type.id, tenant=tenant.id)
            else:
                # Logged in user is making the call, so TenantMixin is applied.
                details = IntegrationDetails.objects.get(type=integration_type.id)
        except IntegrationDetails.DoesNotExist:
            details = None

    if details:
        storage = Storage(IntegrationCredentials, 'details', details, 'credentials')
        credentials = storage.get()
        expiry_date = timezone.now() + timedelta(days=7)

        if credentials.expires and expiry_date > credentials.expires:
            # Credentials have expired, so refresh the token.
            credentials = get_access_token(credentials, integration_type)
    else:
        credentials = None

    return credentials


def put_credentials(integration_type, credentials):
    """
    Store new information for the given credentials.

    Args:
        integration_type (str): Name of the integration for which the storage should be retrieved.
        credentials (IntegrationCredentials): Updated credentials object.
    """
    integration_type = IntegrationType.objects.get(name__iexact=integration_type)
    details = IntegrationDetails.objects.get(type=integration_type.id)

    storage = Storage(IntegrationCredentials, 'details', details, 'credentials')
    storage.put(credentials)


def get_access_token(credentials, integration_type, code=None):
    """
    Generic function to retrieve an OAuth 2.0 access token.

    Args:
        credentials (object): Contains the OAuth 2.0 credentials needed to retrieve a token.
        integration_type (str): Name of the integration for which the credentials should be retrieved.
        code (str, optional): Authorization code which will be exchanged for an access token.

    Returns:
        credentials (object): Updated credentials with a new access token.
    """
    payload = {
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
    }

    if code:
        # Trade the auth code for an access token.
        payload.update({'grant_type': 'authorization_code', 'redirect_uri': credentials.redirect_uri, 'code': code})
    else:
        # Already authenticated once, but access token expired.
        payload.update({'grant_type': 'refresh_token', 'refresh_token': credentials.refresh_token})

    if isinstance(integration_type, basestring):
        # Sometimes we pass just a string, so fetch the actual integration type.
        integration_type = IntegrationType.objects.get(name__iexact=integration_type)

    response = requests.post(
        url=integration_type.token_url,
        data=payload,
    )

    if response.status_code == 200:
        is_slack = integration_type.name.lower() == 'slack'
        data = response.json()

        expires = data.get('expires_in')

        credentials.access_token = data.get('access_token')
        credentials.refresh_token = data.get('refresh_token')

        if expires:
            credentials.expires = timezone.now() + timedelta(seconds=expires)

        if is_slack:
            # Store the team ID so we can use it later for authorization.
            details = SlackDetails.objects.get(type=integration_type.id)
            details.team_id = data.get('team_id')
            details.save()
        else:
            details = IntegrationDetails.objects.get(type=integration_type.id)

        storage = Storage(IntegrationCredentials, 'details', details, 'credentials')
        storage.put(credentials)

        return credentials
    else:
        return None


class LilyOAuthCredentials(Credentials):
    def __init__(
        self,
        client_id,
        client_secret,
        redirect_uri,
        access_token=None,
        refresh_token=None,
        expires=None,
        integration_context=None
    ):
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.refresh_token = refresh_token
        self.expires = expires
        self.integration_context = integration_context
