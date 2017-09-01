from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from lily.contacts.models import Contact
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
            'columns_for_item': ['tags']
        },
    }

    # ExportListViewMixin
    def value_for_column(self, contact, column):
        try:
            if column == 'url':
                return '/#/contacts/%s' % contact.id
            elif column == 'accounts':
                # 'accounts' is a dict, so we need to process it differently.
                value = [account.name for account in contact.accounts.all()]
            elif column == 'email_addresses':
                # 'email_addresses' is a dict, so we need to process it differently.
                value = [email.email_address for email in contact.email_addresses.all()]
            elif column == 'phone_numbers':
                # 'phone_numbers' is a dict, so we need to process it differently.
                value = [phone_number.number for phone_number in contact.phone_numbers.all()]
            elif column == 'tags':
                value = [tag.name for tag in contact.tags.all()]
            else:
                value = getattr(contact, column)

            if isinstance(value, list):
                value = ', '.join(value)
        except KeyError:
            value = ''
        return value

    def get_queryset(self):
        return Contact.objects.all()
