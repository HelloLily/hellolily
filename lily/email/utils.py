from django.db.models import Q

from email_wrapper_lib.models import EmailAccount


def get_email_accounts(user):
    # TODO: figure out which way to query is faster.

    # email_account_ids = EmailAccountConfig.objects.filter(
    #     Q(owners=user) |
    #     Q(shared_with_users=user) |
    #     Q(shared_with_teams=user.teams.all()) |
    #     Q(shared_with_everyone=True)
    # ).distinct().values_list(
    #     'email_account_id',
    #     flat=True
    # )
    # return EmailAccount.objects.filter(
    #     id__in=email_account_ids
    # )

    return EmailAccount.objects.filter(
        Q(config__owners=user) |
        Q(config__shared_with_users=user) |
        Q(config__shared_with_teams=user.teams.all()) |
        Q(config__shared_with_everyone=True)
    )
