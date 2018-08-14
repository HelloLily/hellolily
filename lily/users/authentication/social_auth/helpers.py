import datetime
import json

import jwt
from django.urls import reverse
from jwt.algorithms import RSAAlgorithm
from requests_cache import CachedSession
from requests_oauthlib import OAuth2Session

from .providers.google import GoogleAuthProvider
from .providers.microsoft import MicrosoftAuthProvider

SOCIAL_AUTH_PROVIDERS = {
    'google': GoogleAuthProvider,
    'microsoft': MicrosoftAuthProvider,
}


def get_authorization_url(request, provider_name):
    provider = SOCIAL_AUTH_PROVIDERS[provider_name]()

    oauth_session = OAuth2Session(
        client_id=provider.client_id,
        scope=provider.scope,
        redirect_uri=request.build_absolute_uri(
            reverse('social_login_callback', kwargs={'provider_name': provider_name})
        ),
    )
    authorization_url, state = oauth_session.authorization_url(url=provider.auth_uri)
    request.session['social_login_state'] = state

    return authorization_url


def get_profile(request, provider_name):
    provider = SOCIAL_AUTH_PROVIDERS[provider_name]()

    # Prepare the session for fetching the token.
    session = OAuth2Session(
        client_id=provider.client_id,
        scope=provider.scope,
        state=request.session.get('social_login_state', ''),
        redirect_uri=request.build_absolute_uri(
            reverse('social_login_callback', kwargs={'provider_name': provider_name})
        ),
    )

    # Clear the session state data before continuing.
    if 'social_login_state' in request.session:
        del request.session['social_login_state']

    # Go and fetch the oauth token.
    token = session.fetch_token(
        token_url=provider.token_uri,
        client_secret=provider.client_secret,
        authorization_response=request.build_absolute_uri()
    )

    # Get the id_token from the oauth token.
    unparsed_id_token = token['id_token']

    # Retrieve the certificates from the provider, this is in json format and is cached for 1 hour.
    expire_after = datetime.timedelta(hours=1)
    cached_session = CachedSession(backend='memory', expire_after=expire_after)
    provider_certificates = cached_session.get(provider.jwks_uri).json().get('keys')

    # Put the certificates in a dict, with the identifier as key.
    certificate_set = {cert['kid']: cert for cert in provider_certificates}

    # Look up which certificate was used to sign the id_token.
    kid = jwt.get_unverified_header(unparsed_id_token).get('kid')

    # Convert the certificate from json to something the jwt library can use.
    certificate = RSAAlgorithm.from_jwk(json.dumps(certificate_set[kid]))

    # Now finally do the actual decoding and verifying.
    id_token = jwt.decode(unparsed_id_token, certificate, audience=provider.client_id)

    # Put the parsed id_token in the response.
    token['id_token'] = id_token

    return provider.parse_profile(session, token)
