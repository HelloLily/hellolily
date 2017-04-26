from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from lily.accounts.models import Account, AccountStatus, Website
from lily.cases.models import Case, CaseType, CaseStatus
from lily.deals.models import DealContactedBy, DealFoundThrough, DealNextStep, DealWhyCustomer, DealWhyLost, DealStatus
from lily.contacts.models import Contact, Function
from lily.socialmedia.models import SocialMedia
from lily.tenant.models import Tenant
from lily.users.models import LilyUser, Team
from lily.utils.models.models import EmailAddress


class Command(BaseCommand):
    def handle(self, **options):
        """
        Create a new tenant and fill it with sensible default values.
        """
        tenant_name = raw_input('Enter name for the new Tenant: ')
        tenant_country = raw_input('Enter the country for the new Tenant [NL]: ') or 'NL'
        print ''
        print 'Thank you! creating the Tenant now!'
        print ''

        with transaction.atomic():
            tenant = Tenant.objects.create(name=tenant_name, country=tenant_country)

            # Team
            team_list = ['Sales', 'Customer care', 'Finance', ]
            print 'Adding user teams.'
            for team in team_list:
                Team.objects.create(tenant=tenant, name=team)

            # AccountStatus
            account_status_list = ['Customer', 'Relation', 'Prospect', 'Former customer', ]
            print 'Adding account status options.'
            for position, name in enumerate(account_status_list, start=1):
                AccountStatus.objects.create(tenant=tenant, position=position, name=name)

            # CaseType
            case_type_list = ['Callback', 'Support', 'Finance', 'Sales', 'Other', ]
            print 'Adding case types.'
            for name in case_type_list:
                CaseType.objects.create(tenant=tenant, name=name)

            # CaseStatus
            case_status_list = ['New', 'Processing', 'Pending input', 'Follow up', 'Closed', ]
            print 'Adding case status options.'
            for position, name in enumerate(case_status_list, start=1):
                CaseStatus.objects.create(tenant=tenant, position=position, name=name)

            # DealContactedBy
            deal_contact_by_list = ['Phone', 'Website form', 'Email', 'Chat', 'Social media', 'Exhibition', 'Other', ]
            print 'Adding deal contacted by options.'
            for position, name in enumerate(deal_contact_by_list, start=1):
                DealContactedBy.objects.create(tenant=tenant, position=position, name=name)

            # DealFoundThrough
            deal_found_through_list = [
                'Search engine', 'Social media', 'Talk with employee', 'Existing customer', 'Cold calling',
                'Public speaking', 'Press and articles', 'Exhibition', 'Radio/TV', 'Other',
            ]
            print 'Adding deal found through options.'
            for position, name in enumerate(deal_found_through_list, start=1):
                DealFoundThrough.objects.create(tenant=tenant, position=position, name=name)

            # DealNextStep
            deal_next_step_dict = {
                'Contact': '2',
                'Follow up': '5',
                'Waiting on client': '5',
                'Aftersales': '15',
                'None': '0'
            }
            print 'Adding deal next steps.'
            for position, name in enumerate(deal_next_step_dict, start=1):
                date_increment = deal_next_step_dict.get(name)
                DealNextStep.objects.create(tenant=tenant, position=position, name=name, date_increment=date_increment)

            # DealWhyCustomer
            deal_why_customer_list = ['Unknown', 'Other', ]
            print 'Adding deal why customer options.'
            for position, name in enumerate(deal_why_customer_list, start=1):
                DealWhyCustomer.objects.create(tenant=tenant, position=position, name=name)

            # DealWhyLost
            deal_why_lost_list = [
                'Too expensive', 'No response after inquiry', 'No response to quote', 'We replied too late',
                'Not a customer for us', 'Missing features', 'Other',
            ]
            print 'Adding deal why lost options.'
            for position, name in enumerate(deal_why_lost_list, start=1):
                DealWhyLost.objects.create(tenant=tenant, position=position, name=name)

            # DealStatus
            deal_status_list = ['Open', 'Won', 'Lost', ]
            print 'Adding deal status options.'
            for position, name in enumerate(deal_status_list, start=1):
                DealStatus.objects.create(tenant=tenant, position=position, name=name)

            # Team Lily
            print 'Adding Team Lily to the tenant.'
            email_address = EmailAddress.objects.create(
                email_address='support@hellolily.com',
                status=EmailAddress.PRIMARY_STATUS,
                tenant=tenant,
            )

            account_status = AccountStatus.objects.get(name='Relation', tenant=tenant)

            account = Account.objects.create(
                tenant=tenant,
                name='Team Lily',
                description=(
                    'Team Lily has been added automatically. Feel free to add all the other companies,'
                    'organizations and other parties you get in touch with as Accounts.'
                ),
                status=account_status,
            )

            website = Website.objects.create(
                website='https://hellolily.com',
                is_primary=True,
                account=account,
                tenant=tenant,
            )

            twitter = SocialMedia.objects.create(
                tenant=tenant,
                name='twitter',
                username='sayhellolily',
                profile_url='https://twitter.com/sayhellolily',
            )

            account.email_addresses.add(email_address)
            account.websites.add(website)
            account.social_media.add(twitter)

            # Add Team Lily default contacts
            print 'Adding default contacts to Team Lily.'
            lily_contacts = [{
                'first_name': 'Sjoerd',
                'last_name': 'Romkes',
                'email_address': 'sjoerd@hellolily.com',
            }]

            for contact in lily_contacts:
                contact_instance = Contact.objects.create(
                    tenant=tenant,
                    gender=0,
                    first_name=contact['first_name'],
                    last_name=contact['last_name'],
                )

                contact_email = EmailAddress.objects.create(
                    email_address=contact['email_address'],
                    status=EmailAddress.PRIMARY_STATUS,
                    tenant=tenant,
                )
                Function.objects.create(account=account, contact=contact_instance)
                contact_instance.email_addresses.add(contact_email)

            print 'Adding first case'

            description = (
                'A case can be used for tasks which take more than a couple of minutes to complete.'
                '\nFor example extensive customer service or technical questions.'
                '\n\nTo solve this case, send an email to Team Lily with your first thoughts, concerns or questions.'
                '\nAfterwards, close this case by clicking \'Closed\' since you\'ve solved it.'
                '\nThat\'s it, you\'ve completed your first case!'
            )

            Case.objects.create(
                account=account,
                contact=Contact.objects.filter(tenant=tenant).first(),
                subject='Team Lily needs your input!',
                description=description,
                status=CaseStatus.objects.get(name='New', tenant=tenant),
                type=CaseType.objects.get(name='Support', tenant=tenant),
                priority=Case.LOW_PRIO,
                expires=date.today() + timedelta(days=7),
                assigned_to=LilyUser.objects.filter(tenant=tenant).first(),
                tenant=tenant,
            )

            print ''
            print 'All done!'
            print 'You can now add users to tenant %s - %s' % (tenant.pk, tenant.name)
            print ''
