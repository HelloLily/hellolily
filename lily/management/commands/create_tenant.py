from django.core.management.base import BaseCommand

from lily.accounts.models import AccountStatus
from lily.cases.models import CaseType, CaseStatus
from lily.deals.models import DealContactedBy, DealFoundThrough, DealNextStep, DealWhyCustomer, DealWhyLost, DealStatus
from lily.tenant.models import Tenant
from lily.users.models import LilyGroup


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

        tenant = Tenant.objects.create(name=tenant_name, country=tenant_country)

        # LilyGroups
        lily_group_list = ['Sales', 'Customer care', 'Finance', ]
        print 'Adding user groups.'
        for lily_group in lily_group_list:
            LilyGroup.objects.create(tenant=tenant, name=lily_group)

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

        print ''
        print 'All done!'
        print 'You can now add users to tenant %s - %s' % (tenant.pk, tenant.name)
        print ''
