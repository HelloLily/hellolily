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
        'url': {
            'headers': [_('url')],
            'columns_for_item': ['url']
        },
        'name': {
            'headers': [_('Account')],
            'columns_for_item': ['name']
        },
        'contactInformation': {
            'headers': [
                _('Email'),
                _('Phone numbers'),
                _('Addresses'),
            ],
            'columns_for_item': [
                'email_addresses',
                'phone_numbers',
                'addresses',
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
        },
        'status': {
            'headers': [_('Status')],
            'columns_for_item': ['status']
        },
    }

    # ExportListViewMixin
    def value_for_column(self, account, column):
        try:
            if column == 'url':
                return '/#/accounts/%s' % account['id']
            elif column == 'email_addresses':
                # 'email_addresses' is a dict, so we need to process it differently.
                value = []
                for email in account.get('email_addresses', []):
                    value.append(email['email_address'])
            elif column == 'phone_numbers':
                # 'phone_numbers' is a dict, so we need to process it differently.
                value = []
                for phone_number in account.get('phone_numbers', []):
                    value.append(phone_number['number'])
            else:
                value = account[column]
        except KeyError:
            result = ''
        else:
            # Fetch address info from database
            if column == 'addresses':
                result = '\r\n'.join(['%s, %s, %s, %s' % (
                    address['address'] or '',
                    address['postal_code'] or '',
                    address['city'] or '',
                    address['country'] or '',
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
