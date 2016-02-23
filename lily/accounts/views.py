from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from lily.search.lily_search import LilySearch
from lily.utils.views.mixins import ExportListViewMixin


class ExportAccountView(ExportListViewMixin, View):
    """
    View to make export of accounts possible
    """
    http_method_names = ['get']
    file_name = 'accounts.csv'

    # ExportListViewMixin
    exportable_columns = {
        'id': {
            'headers': [_('ID')],
            'columns_for_item': ['id']
        },
        'name': {
            'headers': [_('Account')],
            'columns_for_item': ['name']
        },
        'contactInformation': {
            'headers': [
                _('Email'),
                _('Work Phone'),
                _('Mobile Phone'),
                _('Address'),
            ],
            'columns_for_item': [
                'email_addresses',
                'phone_work',
                'phone_mobile',
                'address',
            ]
        },
        'assignedTo': {
            'headers': [_('Assigned to')],
            'columns_for_item': ['assigned_to']
        },
        'created': {
            'headers': [_('Created')],
            'columns_for_item': ['created']
        },
        'modified': {
            'headers': [_('Modified')],
            'columns_for_item': ['modified']
        },
        'tags': {
            'headers': [_('Tags')],
            'columns_for_item': ['tag']
        },
        'customerId': {
            'headers': [_('Customer ID')],
            'columns_for_item': ['customer_id']
        }
    }

    # ExportListViewMixin
    def value_for_column(self, account, column):
        try:
            if column == 'email_addresses':
                # 'email_addresses' is a dict, so we need to process it differently
                value = []
                for account in account.get('email_addresses', []):
                    value.append(account['email_address'])
            else:
                value = account[column]
        except KeyError:
            result = ''
        else:
            # Fetch address info from database
            if column == 'address':
                result = '\r\n'.join(['%s %s %s, %s, %s, %s' % (
                    address['address_street'] or '',
                    address['address_street_number'] or '',
                    address['address_complement'] or '',
                    address['address_postal_code'] or '',
                    address['address_city'] or '',
                    address['address_country'] or '',
                ) for address in value])
            elif isinstance(value, list):
                result = ', '.join(value)
            else:
                result = value
        return result

    # ExportListViewMixin
    def get_items(self):
        search = LilySearch(
            tenant_id=self.request.user.tenant_id,
            model_type='accounts_account',
            page=0,
            size=1000000000,
        )
        if self.request.GET.get('export_filter'):
            search.query_common_fields(self.request.GET.get('export_filter'))
        return search.do_search()[0]
