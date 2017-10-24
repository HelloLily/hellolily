from oauth2client.contrib.django_orm import Storage

from email_wrapper_lib.models.models import EmailAccount


def create_account_from_code(provider, code):
    credentials = provider.flow.step2_exchange(code=code)
    connector = provider.connector(credentials, 'me')
    profile = connector.profile.get()
    connector.execute()

    account, created = EmailAccount.objects.get_or_create(
        username=profile['username'],
        user_id=profile['user_id'],
        provider_id=provider.id,
    )

    # Set the store so the credentials will auto refresh.
    credentials.set_store(Storage(EmailAccount, 'id', account.pk, 'credentials'))

    account.credentials = credentials

    # TODO: set the status to RESYNC if necesary.

    account.save(update_fields=['credentials'])

    return account
