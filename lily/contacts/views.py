from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from lily.search.lily_search import LilySearch
from lily.utils.views.mixins import ExportListViewMixin


class ExportContactView(LoginRequiredMixin, ExportListViewMixin, View):
    http_method_names = ['get']
    file_name = 'contacts.csv'

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
            'headers': [_('Name')],
            'columns_for_item': ['full_name']
        },
        'contactInformation': {
            'headers': [
                _('Email'),
                _('Phone numbers'),
            ],
            'columns_for_item': [
                'email_addresses',
                'phone_numbers',
            ]
        },
        'worksAt': {
            'headers': [_('Works at')],
            'columns_for_item': ['accounts']
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
    }

    # ExportListViewMixin
    def value_for_column(self, contact, column):
        try:
            if column == 'url':
                return '/#/contacts/%s' % contact['id']
            elif column == 'accounts':
                # 'accounts' is a dict, so we need to process it differently.
                value = []
                for account in contact.get('accounts', []):
                    value.append(account['name'])
            elif column == 'email_addresses':
                # 'email_addresses' is a dict, so we need to process it differently.
                value = []
                for email in contact.get('email_addresses', []):
                    value.append(email['email_address'])
            elif column == 'phone_numbers':
                # 'phone_numbers' is a dict, so we need to process it differently.
                value = []
                for phone_number in contact.get('phone_numbers', []):
                    value.append(phone_number['number'])
            else:
                value = contact[column]

            if isinstance(value, list):
                value = ', '.join(value)
        except KeyError:
            value = ''
        return value

    # ExportListViewMixin
    def get_items(self):
        search = LilySearch(
            tenant_id=self.request.user.tenant_id,
            model_type='contacts_contact',
            page=0,
            size=1000000000,
        )

        if self.request.GET.get('export_filter'):
            search.query_common_fields(self.request.GET.get('export_filter'))
        return search.do_search()[0]
