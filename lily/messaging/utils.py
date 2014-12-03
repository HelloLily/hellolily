from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from lily.messaging.models import MessagesAccount, PRIVATE, PUBLIC, SHARED
from lily.utils.functions import uniquify


def get_messages_accounts(user, model_cls=None, pk_list=None):
    """
    Returns a list of the users accounts and accounts that are shared with
    this user.

    Also filters out accounts that are deleted and/or have wrong credentials.

    Arguments:
        user: the user instance for which to get the messages accounts
        model_cls (optional): filters the accounts on a specific model class
        pk_list (optional): filters the accounts on specific pks

    Returns:
        List of MessagesAccounts.
    """
    # Check cache
    if hasattr(user, '_messages_accounts_%s_%s' % (model_cls, pk_list)):
        return getattr(user, '_messages_accounts_%s_%s' % (model_cls, pk_list))

    messages_accounts = MessagesAccount.objects.filter(
        Q(is_deleted=False) &
        (
            Q(shared_with=PRIVATE, owner=user) |
            Q(shared_with=PUBLIC) |
            Q(shared_with=SHARED, user_group__pk=user.pk)
        )
    )

    # Filter by content type if provided
    if model_cls is not None:
        ctype = ContentType.objects.get_for_model(model_cls)
        messages_accounts = messages_accounts.filter(Q(polymorphic_ctype=ctype))

    if pk_list is not None:
        messages_accounts = messages_accounts.filter(Q(pk__in=pk_list))

    messages_accounts = messages_accounts.order_by('emailaccount__email').distinct('emailaccount__email')

    # Cache for this request.
    setattr(user, '_messages_accounts_%s_%s' % (model_cls, pk_list), messages_accounts)

    return messages_accounts
