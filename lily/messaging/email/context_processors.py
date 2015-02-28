from .utils import email_auth_update, unread_emails
from lily.utils.functions import is_ajax


def email(request):
    """
    Add extra context variables for email.
    """
    extra_context = {}
    if not is_ajax(request) and not request.user.is_anonymous():
        extra_context.update({'email_auth_update': email_auth_update(request.user)})
        # TODO: slow queries, temporary disable unread_emails
        # extra_context.update({'unread_emails': unread_emails(request.user)})
    return extra_context
