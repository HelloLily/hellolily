from django.core.management.base import BaseCommand

from lily.accounts.models import Account


class Command(BaseCommand):
    help = """Find duplicates in functions for each account and contact and remove them"""

    def handle(self, **kwargs):
        accounts = Account.objects.all()

        functions_flat = set()
        accounts_size = accounts.count()
        for i, account in enumerate(accounts.iterator()):
            for function in account.functions.iterator():
                function_flat = '%s-%s' % (function.account_id, function.contact_id)
                if function_flat in functions_flat:
                    function.delete(hard=True)
                else:
                    functions_flat.add(function_flat)

            print '%s > %s' % (i + 1, accounts_size)
