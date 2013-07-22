from django.core.urlresolvers import reverse
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from python_imap.folder import INBOX, SENT, DRAFTS, TRASH, SPAM

from lily.messaging.email.models import EmailAccount
from lily.tenant.middleware import get_current_user


class EmailMiddleware(object):

    def process_template_response(self, request, response):
        """
        Add a JSON-structu with the structure and other information about
        e-mail folders.

        Example output:
        [{
            'Inbox': {
                'is_parent': False,
                'show_all': True,
                'children': {},
            },
            'Prospects': {
                'is_parent': True,
                'show_all': False,
                'children': {
                    'Folder A': {
                        'is_parent': False,
                        'children': {},
                    },
                    'Folder B': {
                        'is_parent': False,
                        'children': {},
                    },
                },
            }
        }]
        """
        if request.path.startswith(reverse('admin:index')) or not request.user or request.user.is_anonymous():
            return response

        email_folders = SortedDict()  # Preserve folder order

        # First, add default folders in order
        default_folders = SortedDict([
            (_(u'Inbox'), INBOX),
            (_(u'Sent'), SENT),
            (_(u'Drafts'), DRAFTS),
            (_(u'Trash'), TRASH),
            (_(u'Spam'), SPAM),
        ])

        for folder_name, folder_identifier in default_folders.items():
            email_folders[folder_name] = {
                'flags': [folder_identifier],
                'show_all': True,
                'is_parent': False,
                'children': {},
            }

        email_accounts = get_current_user().get_messages_accounts(EmailAccount)

        for account in email_accounts:
            # Set root folders for email address
            account_root_folders = get_email_folders_structure(account.folders)
            email_folders[account.email.email_address] = {
                'flags': ['\\Noselect'],
                'show_all': False,
                'is_parent': True,
                'children': account_root_folders,
            }

            # Remove sub folders from root
            for root_folder_name, root_folder in account_root_folders.items():
                if root_folder.get('is_parent'):
                    email_folders[account.email.email_address]['children'][root_folder_name]['account_id'] = account.pk

                    for sub_folder_name, sub_folder in root_folder.get('children').items():
                        if sub_folder_name in account_root_folders.keys():
                            del account_root_folders[sub_folder_name]
                            continue
                        email_folders[account.email.email_address]['children'][root_folder_name]['children'][sub_folder_name]['account_id'] = account.pk
                else:
                    # Might have been deleted if it was a duplicate
                    if root_folder_name in email_folders[account.email.email_address]['children']:
                        email_folders[account.email.email_address]['children'][root_folder_name]['account_id'] = account.pk

        response.context_data.update({'email_folders': email_folders})
        return response


def get_email_folders_structure(data):
    folders = SortedDict()
    sorted_folders = sorted(data, key=unicode.lower)
    for folder_name in sorted_folders:
        folder = data[folder_name]
        if len(set([INBOX, SENT, DRAFTS, TRASH, SPAM]).intersection(set(folder.get('flags', [])))) > 0:
            continue
        folders[folder_name] = folder
        if folder.get('children', False) or False:
            folders[folder_name]['children'] = get_email_folders_structure(folder.get('children'))

    return folders
