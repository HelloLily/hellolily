from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from lily.accounts.models import Account
from lily.utils.views.mixins import ExportListViewMixin


class ExportAccountView(LoginRequiredMixin, ExportListViewMixin, View):
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
            'columns_for_item': ['tags']
        },
        'customerId': {
            'headers': [_('Customer ID')],
            'columns_for_item': ['customer_id']
        }
    }

    # ExportListViewMixin
    def value_for_column(self, account, column):
        try:
            if column == 'url':
                return '/#/accounts/%s' % account.id
            elif column == 'email_addresses':
                # 'email_addresses' is a dict, so we need to process it differently.
                value = [email.email_address for email in account.email_addresses.all()]
            elif column == 'phone_numbers':
                # 'phone_numbers' is a dict, so we need to process it differently.
                value = [phone_number.number for phone_number in account.phone_numbers.all()]
            elif column == 'addresses':
                value = '\r\n'.join(['%s, %s, %s, %s' % (
                    address.address,
                    address.postal_code,
                    address.city,
                    address.get_country_display(),
                ) for address in account.addresses.all()])
            elif column == 'tags':
                value = [tag.name for tag in account.tags.all()]
            else:
                value = getattr(account, column)
        except KeyError:
            result = ''
        else:
            if isinstance(value, list):
                result = ', '.join(value)
            else:
                result = value
        return result

    def get_queryset(self):
        return Account.objects.all()
