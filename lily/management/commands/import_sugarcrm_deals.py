import csv
from collections import defaultdict
from datetime import datetime
from pprint import pformat

from django.core.management.base import BaseCommand

from lily.accounts.models import Account
from lily.deals.models import Deal
from lily.tenant.models import Tenant
from lily.users.models import LilyUser

from . import user_map  # load externally to prevent adding users to codebase


class Command(BaseCommand):
    help = """Load Sugar CRM deals into an existing tenant."""

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            dest='tenant',
            action='store',
            default='',
            help='Specify a tenant to import the data in.'
        )
        parser.add_argument(
            '--dry-run',
            dest='dry_run',
            action='store_true',
            help='If only output should be printed without actually changed the db.'
        )
        parser.add_argument(
            '--imported-from',
            dest='imported_from',
            action='store',
            default='',
            help='Specify an imported_from value.'
        )

    def handle(self, *args, **options):
        '''Main method for iterating over all deals in the csv.'''
        tenant_option = options.get('tenant')
        if not tenant_option:
            raise Exception('Need tenant option.')
        self.tenant = Tenant.objects.get(pk=int(tenant_option.strip()))
        self.stdout.write('Using tenant %s' % self.tenant.id)

        self.user_map = user_map.get_user_map()

        self.imported_from = options.get('imported_from')
        if not self.imported_from:
            raise Exception('Need "imported from" option!')

        self.dry_run = options.get('dry_run')
        if self.dry_run:
            self.stdout.write('Dry running.')

        if args:
            self.stdout.write('Aborting, unexpected arguments %s' % list(args))
            return

        count = defaultdict(lambda: 0)
        with open('deals.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            csvfile.readline()  # skip header
            for i, row in enumerate(reader):
                # === Read inputs. ===

                subject = row[0]
                # sugar_id = row[1]
                opportunity_amount = self.clean_amount(row[2])
                # currency = row[3]
                closing_date = None
                try:
                    closing_date = datetime.strptime(row[4], '%d-%m-%Y')
                except:
                    pass

                stage = {'Called': 4, 'Closed Lost': 3, 'Closed Won': 2, 'MailSend': 5, 'Negotiation/Review': -1,
                         'Proposal/Price Quote': 1, 'Special': -2}.get(row[5])
                if stage <= 0:
                    count['stage_invalid'] += 1
                # probability = row[6]
                # next_action = row[7]
                new_business = 'Existing Business' == row[8]
                account_name = row[9]
                account = None
                try:
                    account = Account.objects.get(tenant=self.tenant, name=account_name)
                except Account.MultipleObjectsReturned:
                    count['account_returns_multiple'] += 1
                except Account.DoesNotExist:
                    count['account_does_not_exist'] += 1
                description = row[10]
                # amount = row[11]
                # lead_source = row[12]
                # campaign_id = row[13]
                user_name = row[14]
                lily_user = None
                try:
                    lily_email = self.user_map[user_name]
                    try:
                        lily_user = LilyUser.objects.get(tenant=self.tenant, email=lily_email)
                    except LilyUser.DoesNotExist:
                        count['lily_user_does_not_exist'] += 1
                except KeyError:
                    count['assigned_none'] += 1
                # user_id = row[15]
                created_date = datetime.strptime(row[16].split(' ')[0], '%d-%m-%Y')
                modified_date = datetime.strptime(row[17].split(' ')[0], '%d-%m-%Y')
                # id_created = row[18]
                # id_modified = row[19]
                # deleted = row[20]
                monthly_amount = self.clean_amount(row[21])
                # hw_amount = row[22]
                one_off_amount = self.clean_amount(row[23])
                twitter_followed = 'CheckFollowed' == row[24]
                card_send = {'': False, '0': False, '1': True}[row[25]]
                feedback_form_send = {'': False, '0': False, '1': True}[row[26]]

                # === Combine inputs. ===

                if not one_off_amount and not opportunity_amount:
                    combined_one_off_amount = opportunity_amount
                else:
                    combined_one_off_amount = one_off_amount

                if stage in [Deal.WON_STAGE, Deal.LOST_STAGE]:
                    if closing_date is None:
                        if stage == Deal.WON_STAGE:
                            closing_date = created_date
                            count['no_closing_date_for_won'] += 1
                        else:
                            closing_date = modified_date
                            count['no_closing_date_for_lost'] += 1
                    assert closing_date, 'The closing_date should be repaired.'
                else:
                    closing_date = None

                # Print a nicely formatted line for the deal.
                self.stdout.write(pformat((
                    subject.ljust(50), (closing_date.strftime('%Y-%m-%d') if closing_date else '').ljust(10),
                    (unicode(Deal.STAGE_CHOICES[stage][1]) if stage > 0 else 'INVALID').ljust(15),
                    account_name.ljust(40), 'new'.ljust(6) if new_business else 'exists', lily_user,
                    created_date.strftime('%Y-%m-%d'), modified_date.strftime('%Y-%m-%d'),
                    monthly_amount.rjust(4), combined_one_off_amount.rjust(4),
                    ('%sfollowed' % ('' if twitter_followed else 'not ')).ljust(12),
                    ('card %ssent' % ('' if card_send else 'not ')).ljust(13),
                    ('feedback %ssent' % ('' if feedback_form_send else 'not ')).ljust(17),
                    description), width=10000))

                # === Create the deal. ===

                if account and lily_user:
                    count['created'] += 1
                    if not self.dry_run:
                        deal = Deal.objects.create(
                            is_archived=True, imported_from=self.imported_from, tenant=self.tenant, account=account,
                            assigned_to=lily_user, created=created_date, modified=modified_date, name=subject,
                            amount_once=combined_one_off_amount, amount_recurring=monthly_amount,
                            twitter_checked=twitter_followed, new_business=new_business,
                            card_sent=card_send, feedback_form_sent=feedback_form_send, description=description
                        )
                        if closing_date:
                            deal.closed_date = closing_date
                        if stage > 0:
                            deal.stage = stage
                        deal.save()

        self.stdout.write(pformat(dict(count)))

    def clean_amount(self, amount):
        """Returns a cleaned, normalized amount in full Euros."""
        amount = amount.lstrip('\xe2\x82\xac')  # euro sign
        amount = amount.replace('.', '').replace(',', '')
        return str(int(amount) / 100)
