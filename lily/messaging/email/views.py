import datetime
import email
import os
import traceback
import urllib
import logging
from email import Encoders
from email.MIMEBase import MIMEBase

from bs4 import BeautifulSoup
from dateutil.tz import tzutc
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.files.storage import default_storage
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.core.servers.basehttp import FileWrapper
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404, render_to_response
from django.template.defaultfilters import truncatechars
from django.utils import simplejson
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from django.views.generic.base import View, TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView
from imapclient.imapclient import DRAFT
from python_imap.folder import DRAFTS, INBOX, SENT, TRASH, SPAM, ALLMAIL, IMPORTANT, STARRED
from python_imap.logger import logger as imap_logger
from python_imap.server import IMAP
from python_imap.utils import convert_html_to_text, parse_search_keys

from lily.contacts.models import Contact
from lily.messaging.email.forms import CreateUpdateEmailTemplateForm, \
    EmailTemplateFileForm, ComposeEmailForm, EmailConfigurationWizard_1, \
    EmailConfigurationWizard_2, EmailConfigurationWizard_3, EmailShareForm
from lily.messaging.email.models import EmailAttachment, EmailMessage, EmailAccount, EmailTemplate, EmailProvider, OK_EMAILACCOUNT_AUTH
from lily.messaging.email.tasks import save_email_messages, mark_messages, delete_messages, synchronize_folder, move_messages
from lily.messaging.email.utils import get_email_parameter_choices, TemplateParser, get_attachment_filename_from_url, get_remote_messages, smtp_connect, EmailMultiRelated
from lily.tenant.middleware import get_current_user
from lily.users.models import CustomUser
from lily.utils.functions import is_ajax
from lily.utils.models import EmailAddress
from lily.utils.views import AttachmentFormSetViewMixin, FilteredListMixin, SortedListMixin


log = logging.getLogger('django.request')


class EmailBaseView(View):
    """
    Base for EmailMessageDetailView and EmailFolderView.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Determine which accounts to show messages from.
        """
        self.all_email_accounts = request.user.get_messages_accounts(EmailAccount)
        if kwargs.get('account_id'):
            self.active_email_accounts = request.user.get_messages_accounts(EmailAccount, pk__in=[kwargs.get('account_id')])
        else:
            self.active_email_accounts = self.all_email_accounts

        return super(EmailBaseView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super(EmailBaseView, self).get_context_data(**kwargs)

        # EmailAccounts user has access to
        kwargs.update({
            'list_title': ', '.join([email_account.email.email_address for email_account in self.all_email_accounts]),
        })

        # Folders for default mailboxes
        default_folder_pairs = [
            (INBOX, _(u'Inbox')),
            (SENT, _(u'Sent')),
            (DRAFTS, _(u'Drafts')),
            (TRASH, _(u'Trash')),
            (SPAM, _(u'Spam')),
        ]
        default_folders_reverse_names = {
            INBOX: 'messaging_email_inbox',
            SENT: 'messaging_email_sent',
            DRAFTS: 'messaging_email_drafts',
            TRASH: 'messaging_email_trash',
            SPAM: 'messaging_email_spam',
        }
        default_account_folders_reverse_names = {
            INBOX: 'messaging_email_account_inbox',
            SENT: 'messaging_email_account_sent',
            DRAFTS: 'messaging_email_account_drafts',
            TRASH: 'messaging_email_account_trash',
            SPAM: 'messaging_email_account_spam',
        }
        def is_active_folder(folder_url):
            """
            Check if *folder_url* is currently being displayed by checking against *self.request.path*
            """
            return urllib.unquote_plus(folder_url.encode('utf-8')) == urllib.unquote_plus(self.request.path)

        default_mailbox_folders = []
        for folder_identifier, folder_name in default_folder_pairs:
            folder_url = reverse(default_folders_reverse_names.get(folder_identifier))
            folder_account_url_name = default_account_folders_reverse_names.get(folder_identifier)
            default_mailbox_folders.append({
                'folder_identifier': folder_identifier,
                'folder_active': is_active_folder(folder_url),
                'folder_name': folder_name,
                'folder_url': folder_url,
                'folder_account_url_name': folder_account_url_name,
            })

        kwargs.update({
            'default_mailbox_folders': default_mailbox_folders
        })

        # EmailAccount mailboxes
        kwargs.update({
            'account_mailboxes': [email_account for email_account in self.all_email_accounts],
        })

        # Currently selected mailbox
        if len(self.active_email_accounts) == 1:
            kwargs.update({
                'active_email_address': self.active_email_accounts[0].email.email_address
            })

        return kwargs


class EmailMessageDetailView(EmailBaseView, DetailView):
    model = EmailMessage

    def get_object(self, queryset=None):
        """
        Verify this email message belongs to an account request.user has access to.
        """
        object = super(EmailMessageDetailView, self).get_object(queryset=queryset)
        if object.account not in self.all_email_accounts:
            raise Http404()

        if object.body_html is None or len(object.body_html.strip()) == 0 and (object.body_text is None or len(object.body_text.strip()) == 0):
            server = self.get_from_imap(object)
            server.logout()

            # Re-fetch
            object = super(EmailMessageDetailView, self).get_object(queryset=queryset)

        # Mark as read
        object.is_seen = True
        object.save()

        # Force fetching from header, for some reason this doesn't happen in the templates
        object.from_email

        return object

    def get_context_data(self, **kwargs):
        """
        Remove any parent folder for default mailbox folders
        """
        kwargs = super(EmailMessageDetailView, self).get_context_data(**kwargs)

        default_folder_identifiers = [
            INBOX,
            SENT,
            DRAFTS,
            TRASH,
            SPAM,
        ]
        folder_name = self.object.folder_name
        if self.object.folder_identifier in default_folder_identifiers:
            folder_name = folder_name.split('/')[-1:][0]

        kwargs.update({
              'folder_name': folder_name,
        })

        # Pass message's email account e-mail address
        kwargs.update({
            'active_email_address': self.object.account.email.email_address,
            'active_email_account': self.object.account,
        })

        return kwargs

    def get_from_imap(self, email_message):
        """
        Download an email message from IMAP.
        """
        host = email_message.account.provider.imap_host
        port = email_message.account.provider.imap_port
        ssl = email_message.account.provider.imap_ssl
        server = IMAP(host, port, ssl)
        server.login(email_message.account.username, email_message.account.password)

        imap_logger.info('Searching IMAP for %s in %s' % (email_message.uid, email_message.folder_name))

        message = server.get_message(email_message.uid, ['BODY[]', 'FLAGS', 'RFC822.SIZE', 'INTERNALDATE'],
                                     server.get_folder(email_message.folder_name), readonly=False)
        if message is not None:
            imap_logger.info('Message retrieved, saving in database')
            save_email_messages([message], email_message.account, message.folder)

        return server
email_detail_view = login_required(EmailMessageDetailView.as_view())


class EmailMessageHTMLView(EmailBaseView, DetailView):
    """
    Display an email body in an isolated html. Used in the page of
    EmailMessageDetailView.
    """
    http_method_names = ['get']
    model = EmailMessage
    template_name_suffix = '_isolated'

    def get_context_data(self, **kwargs):
        # Skip context_data from EmailBaseView
        kwargs = super(EmailBaseView, self).get_context_data(**kwargs)
        is_plain = not bool(self.object.body_html)
        body = u''
        if self.object.body_html:
            body = self.object.body_html.encode('utf-8')
        elif self.object.body_text:
            body = self.object.body_text.encode('utf-8')

        kwargs.update({
            'is_plain': is_plain,
            'body': body,
        })

        return kwargs
email_html_view = login_required(EmailMessageHTMLView.as_view())


class EmailFolderView(EmailBaseView, ListView):
    """
    Show a list of e-mail messages in a certain folder.
    """
    paginate_by = 20
    folder_name = None
    folder_identifier = None

    def get(self, request, *args, **kwargs):
        # Determine which folder to show messages from
        if kwargs.get('folder') and not any([self.folder_name, self.folder_identifier]):
            self.folder_name = urllib.unquote_plus(kwargs.get('folder'))

        # If there is no folder in kwargs, try to detect using self.folder_identifier
        default_folder_pairs = {
            INBOX: _(u'Inbox'),
            SENT: _(u'Sent'),
            DRAFTS: _(u'Drafts'),
            TRASH: _(u'Trash'),
            SPAM: _(u'Spam'),
            ALLMAIL: _(u'All mail'),
        }

        # if self.folder_name is None and self.folder_identifier is not None:
        #     self.folder_name = default_folder_pairs.get(self.folder_identifier)
        # else:
        # Get other mailbox folder name
        # if self.folder_name is None:
        #     # Fallback to ALLMAIL
        #     self.folder_identifier = ALLMAIL
        #     self.folder_name = default_folder_pairs.get(self.folder_identifier)
        # else:
        # Strip away parent's folder name
        # self.folder_name = self.folder_name.split('/')[-1:][0]

        # Check if folder name exists for email_accounts
        # XXX: currently checks just one level of nesting
        folder_found = False
        for email_account in self.all_email_accounts:
            for folder_name, folder in email_account.folders.items():
                if self.folder_identifier in folder.get('flags'):
                    folder_found = True

                    # Show the name on the server for default mailbox folders
                    if self.folder_name is None:
                        self.folder_name = folder.get('full_name')
                    break

                if self.folder_name in [folder_name, folder.get('full_name')]:
                    folder_found = True

                    # Try to match folder_identifier
                    if self.folder_identifier is None:
                        if len(set([INBOX, SENT, DRAFTS, TRASH, SPAM, ALLMAIL]).intersection(set(folder.get('flags')))) > 0:
                            self.folder_identifier = set([INBOX, SENT, DRAFTS, TRASH, SPAM, ALLMAIL]).intersection(set(folder.get('flags'))).pop()
                    break

        #         if self.folder_identifier is not None:
        #             if folder_name == self.folder_identifier.lstrip('\\'):
        #                 folder_found = True
        #                 self.folder_locale_name = folder_name
        #                 break

                sub_folders = folder.get('children', {})
                for sub_folder_name, sub_folder in sub_folders.items():
                    if self.folder_identifier in sub_folder.get('flags'):
                        folder_found = True

                        # Show the name on the server for default mailbox folders
                        if self.folder_name is None:
                            self.folder_name = sub_folder_name
                        break

                    if self.folder_name in [sub_folder_name, sub_folder.get('full_name')]:
                        folder_found = True

                        # Try to match folder_identifier
                        if self.folder_identifier is None:
                            if len(set([INBOX, SENT, DRAFTS, TRASH, SPAM, ALLMAIL]).intersection(set(sub_folder.get('flags')))) > 0:
                                self.folder_identifier = set([INBOX, SENT, DRAFTS, TRASH, SPAM, ALLMAIL]).intersection(set(sub_folder.get('flags'))).pop()

                        # Need full name to find the folder on the server
                        self.folder_name = sub_folder.get('full_name')
                        break

        #             if self.folder_identifier is not None:
        #                 if sub_folder_name == self.folder_identifier.lstrip('\\'):
        #                     folder_found = True
        #                     self.folder_name = sub_folder_name
        #                     break

            if not folder_found:
                raise Http404()

        return super(EmailFolderView, self).get(request, *args, **kwargs)

    def get_queryset(self, tried_remote=False):
        """
        Return empty queryset or return it filtered based on folder_name and/or folder_identifier.
        """
        qs = EmailMessage.objects.none()
        if self.folder_name is not None and self.folder_identifier is not None:
            qs = EmailMessage.objects.filter(Q(folder_identifier=self.folder_identifier) | Q(folder_name=self.folder_name))
        elif self.folder_name is not None:
            qs = EmailMessage.objects.filter(folder_name=self.folder_name)
        elif self.folder_identifier is not None:
            qs = EmailMessage.objects.filter(folder_identifier=self.folder_identifier)
        qs = qs.filter(account__in=self.active_email_accounts).extra(select={
            'num_attachments': 'SELECT COUNT(*) FROM email_emailattachment WHERE email_emailattachment.message_id = email_emailmessage.message_ptr_id AND inline=False'
        }).order_by('-sent_date')

        # Try remote fetch when no results have been found locally
        if not tried_remote and len(qs) == 0:
            for email_account in self.active_email_accounts:
                get_remote_messages(email_account, self.folder_identifier or self.folder_name)
            qs = self.get_queryset(tried_remote=True)

        return qs

    def get_context_data(self, **kwargs):
        kwargs = super(EmailFolderView, self).get_context_data(**kwargs)

        folders = SortedDict()
        folders['Postvak In'] = 'Postvak IN'

        if self.folder_identifier not in [SENT, TRASH]:
            # Find folders for visible accounts
            for account in self.active_email_accounts:
                def get_folders_from_tree(tree):
                    for name, folder in tree.items():
                        if folder.get('is_parent'):
                            if '\\Noselect' not in folder.get('flags'):
                                folders[name] = folder.get('full_name')

                            sub_folders = folder.get('children')
                            if len(sub_folders):
                                get_folders_from_tree(sub_folders)
                        elif name in tree:
                            if '\\Noselect' not in folder.get('flags'):
                                intersect = set([INBOX, SENT, DRAFTS, TRASH, SPAM, ALLMAIL, IMPORTANT, STARRED]).intersection(set(folder.get('flags', [])))
                                if len(intersect) > 0:
                                    # If folder already exists, remove it since it probably wasn't added with *intersect* as the key
                                    if folder.get('full_name') in folders.values():
                                        del folders[folders.keys()[folders.values().index(folder.get('full_name'))]]
                                    folders[intersect.pop()] = folder.get('full_name')
                                elif not folder.get('full_name') in folders.values():
                                    # Don't add to avoid duplicates
                                    folders[name] = folder.get('full_name')

                get_folders_from_tree(account.folders)

        # Sort dictionary by value (folder name)
        folders = SortedDict(sorted(folders.items(), key=lambda t: t[1]))

        # Find active folder
        active_move_to_folder = ''
        if self.folder_identifier in [INBOX, SENT, DRAFTS, TRASH, SPAM]:
            for account in self.active_email_accounts:
                for name, folder in account.folders.items():
                    if len(set([INBOX, SENT, DRAFTS, TRASH, SPAM]).intersection(set(folder.get('flags', [])))) > 0:
                        active_move_to_folder = folder.get('full_name')
                        break
        else:
            active_move_to_folder = self.folder_identifier

        kwargs.update({
            'selected_email_account_id': self.kwargs.get('account_id', ''),
            'selected_email_folder': urllib.quote_plus(self.kwargs.get('folder', self.folder_name or self.folder_identifier)),
            'email_search_key': self.kwargs.get('search_key', ''),
            'move_to_folders': folders,
            'active_move_to_folder': active_move_to_folder,

            'folder_name': self.folder_name,
        })

        # Create an url to send search requests to
        search_url_reverse_name = 'messaging_email_search_all'
        search_url_kwargs = {
            'folder': self.folder_identifier or self.folder_name,
        }
        if len(self.active_email_accounts) == 1:
            search_url_kwargs['account_id'] = self.active_email_accounts[0].id
            search_url_reverse_name = 'messaging_email_search'
        kwargs.update({
            'search_action_url': reverse(search_url_reverse_name, kwargs=search_url_kwargs)
        })

        return kwargs
email_account_folder_view = login_required(EmailFolderView.as_view())


class EmailInboxView(EmailFolderView):
    """
    Show a list of messages in folder: INBOX.
    """
    folder_identifier = INBOX
email_inbox_view = login_required(EmailInboxView.as_view())


class EmailSentView(EmailFolderView):
    """
    Show a list of messages in folder: SENT.
    """
    folder_identifier = SENT
email_sent_view = login_required(EmailSentView.as_view())


class EmailDraftsView(EmailFolderView):
    """
    Show a list of messages in folder: DRAFTS.
    """
    folder_identifier = DRAFTS
email_drafts_view = login_required(EmailDraftsView.as_view())


class EmailTrashView(EmailFolderView):
    """
    Show a list of messages in folder: TRASH.
    """
    folder_identifier = TRASH
email_trash_view = login_required(EmailTrashView.as_view())


class EmailSpamView(EmailFolderView):
    """
    Show a list of messages in folder: SPAM.
    """
    folder_identifier = SPAM
email_spam_view = login_required(EmailSpamView.as_view())


#
# EmailTemplate Views.
#

class ListEmailTemplateView(SortedListMixin, FilteredListMixin, ListView):
    model = EmailTemplate
    sortable = [1, 2]
    default_order_by = 2

    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to provide the list item template.
        """
        kwargs = super(ListEmailTemplateView, self).get_context_data(**kwargs)

        kwargs.update({
            'list_item_template': 'messaging/email/mwsadmin/email_template_list_item.html',
        })

        return kwargs
email_templates_list_view = login_required(ListEmailTemplateView.as_view())


class CreateUpdateEmailTemplateView(object):
    form_class = CreateUpdateEmailTemplateForm
    model = EmailTemplate

    def get_context_data(self, **kwargs):
        """
        Provide an url to go back to.
        """
        kwargs = super(CreateUpdateEmailTemplateView, self).get_context_data(**kwargs)
        kwargs.update({
            'parameter_choices': simplejson.dumps(get_email_parameter_choices()),
            'back_url': self.get_success_url(),
        })
        return kwargs

    def get_success_url(self):
        """
        Return to email template list after creating or updating an email template.
        """
        return reverse('emailtemplate_list')


class CreateEmailTemplateView(CreateUpdateEmailTemplateView, CreateView):
    def form_valid(self, form):
        # Show save messages
        message = _('%s (EmailTemplate) has been created')

        # Saves instance
        response = super(CreateEmailTemplateView, self).form_valid(form)

        message %= self.object.subject
        messages.success(self.request, message)

        return response
create_emailtemplate_view = login_required(CreateEmailTemplateView.as_view())


class UpdateEmailTemplateView(CreateUpdateEmailTemplateView, UpdateView):
    def form_valid(self, form):
        # Show save messages
        message = _('%s (EmailTemplate) has been updated')

        # Saves instance
        response = super(UpdateEmailTemplateView, self).form_valid(form)

        message %= self.object.subject
        messages.success(self.request, message)

        return response
update_emailtemplate_view = login_required(UpdateEmailTemplateView.as_view())


class ParseEmailTemplateView(FormView):
    """
    Parse an uploaded template for variables. This view is only used in AJAX calls.
    """
    form_class = EmailTemplateFileForm

    def form_valid(self, form):
        return HttpResponse(simplejson.dumps({
            'error': False,
            'form': form.cleaned_data
        }), mimetype='application/json')

    def form_invalid(self, form):
        # Every form error will show up as a notification later
        for field, error in form.errors.items():
            messages.warning(self.request, error)

        return HttpResponse(simplejson.dumps({
            'error': True
        }), mimetype='application/json')
parse_emailtemplate_view = login_required(ParseEmailTemplateView.as_view())


class EmailMessageUpdateBaseView(View):
    """
    Base for classes that update an EmailMessage in various ways:
    - move to a folder
    - move to trash
    - mark as (un)read

    Can handle more than a single EmailMessage at once.
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        """
        Find out which messages to update.
        """
        try:
            message_ids = request.POST.getlist('ids[]')
            # Wrap it in a list if necessary
            if not isinstance(message_ids, list):
                message_ids = [message_ids]

            # "Handle" these messages. The action to perform is determined
            # by the subclass.
            if len(message_ids) > 0:
                self.request = request
                self.handle_message_update(message_ids)
        except:
            raise Http404()

        return redirect(self.get_success_url())

    def get_success_url(self):
        # Return to whereever the request came from unless a "next" is provided
        if 'next' in self.request.POST:
            success_url = self.request.POST.get('next')
        else:
            success_url = self.request.META.get('HTTP_REFERER')

        return success_url

    def handle_message_update(self, message_ids):
        raise NotImplementedError('Implement by subclassing %s' % self.__class__.__name__)


class MarkEmailMessageAsReadView(EmailMessageUpdateBaseView):
    """
    Mark message as read.
    """
    def handle_message_update(self, message_ids):
        mark_messages.delay(message_ids, read=True)
mark_read_view = login_required(MarkEmailMessageAsReadView.as_view())


class MarkEmailMessageAsUnreadView(EmailMessageUpdateBaseView):
    """
    Mark message as unread.
    """
    def handle_message_update(self, message_ids):
        mark_messages.delay(message_ids, read=False)
mark_unread_view = login_required(MarkEmailMessageAsUnreadView.as_view())


class TrashEmailMessageView(EmailMessageUpdateBaseView):
    """
    Move message to trash.
    """
    def handle_message_update(self, message_ids):
        delete_messages.delay(message_ids)
move_trash_view = login_required(TrashEmailMessageView.as_view())


class MoveEmailMessageView(EmailMessageUpdateBaseView):
    """
    Move messages to selected folder.
    """
    def handle_message_update(self, message_ids):
        if self.request.POST.get('folder', None):
            move_messages.delay(message_ids, self.request.POST.get('folder'))

            if len(message_ids) == 1:
                message = _('Message has been moved')
            else:
                message = _('Messages have been moved')
            messages.success(self.request, message)
        else:
            raise Http404()
move_messages_view = login_required(MoveEmailMessageView.as_view())


#
# EmailMessage compose views (create/edit draft, reply, forward) incl. preview
#
class EmailMessageComposeBaseView(AttachmentFormSetViewMixin, EmailBaseView, FormView, SingleObjectMixin):
    """
    Base for EmailMessageCreateView and EmailMessageReplyView.
    """
    form_class = ComposeEmailForm
    template_name = 'email/emailmessage_compose.html'

    def dispatch(self, request, *args, **kwargs):
        self.pk = kwargs.get('pk', None)
        return super(EmailMessageComposeBaseView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.get_object()
        return super(EmailMessageComposeBaseView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.get_object()
        return super(EmailMessageComposeBaseView, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        self.object = None
        if self.pk:
            self.object = super(EmailMessageComposeBaseView, self).get_object(queryset=queryset)

    def get_queryset(self):
        return EmailMessage.objects.all()

    def get_form_kwargs(self):
        kwargs = super(EmailMessageComposeBaseView, self).get_form_kwargs()
        kwargs['message_type'] = 'new'

        # Provide initial data if we're editing a draft
        if self.object is not None:
            kwargs.update({
                'draft_id': self.object.pk,
                'initial': {
                    'send_from': self.object.from_email,
                    'subject': self.object.subject,
                    'send_to_normal': self.object.to_combined,
                    'send_to_cc': self.object.to_cc_combined,
                    'send_to_bcc': self.object.to_bcc_combined,
                    'body_html': self.object.body_html,
                },
            })
        return kwargs

    def form_valid(self, form):
        """
        Process form to do either of these actions:
            - save a draft
            - discard a draft
            - send an email message
        """
        unsaved_form = form.save(commit=False)

        server = None
        try:
            account = unsaved_form.send_from

            # Login into IMAP already to save, send or discard up ahead.
            host = account.provider.imap_host
            port = account.provider.imap_port
            ssl = account.provider.imap_ssl
            server = IMAP(host, port, ssl)
            server.login(account.username, account.password)

            # Prepare an instance of EmailMultiAlternatives or EmailMultiRelated
            if 'submit-save' in self.request.POST or 'submit-send' in self.request.POST:
                soup = BeautifulSoup(unsaved_form.body_html, 'permissive')

                # Replace the src attribute of inline images with a Content-ID for each image
                inline_application_url = '/messaging/email/attachment/'
                inline_application_images = soup.findAll('img', {
                    'src': lambda src: src and src.startswith(inline_application_url)
                })

                # Mapping {attachment.pk : image element}
                mapped_attachments = {}
                for image in inline_application_images:
                    # Parse attachment pks from image paths
                    pk_and_path = image.get('src')[len(inline_application_url):].rstrip('/')
                    pk = int(pk_and_path.split('/')[0])
                    mapped_attachments[pk] = image

                # Necessary arguments to create an EmailMultiAlternatives/EmailMultiRelated
                kwargs = dict(
                    subject=unsaved_form.subject,
                    from_email=account.email.email_address,
                    to=[unsaved_form.send_to_normal] if len(unsaved_form.send_to_normal) else None,
                    bcc=[unsaved_form.send_to_bcc] if len(unsaved_form.send_to_bcc) else None,
                    connection=None,
                    attachments=None,
                    headers=self.get_email_headers(),
                    alternatives=None,
                    cc=[unsaved_form.send_to_cc] if len(unsaved_form.send_to_cc) else None,
                    body=convert_html_to_text(unsaved_form.body_html, keep_linebreaks=True)
                )

                # Use multipart/alternative when sending just text e-mails (plain and/or html)
                if len(mapped_attachments.keys()) == 0:
                    # Attach an HTML version as alternative to *body*
                    email_message = EmailMultiAlternatives(**kwargs)
                    email_message.attach_alternative(unsaved_form.body_html, 'text/html')
                else:
                    # Use multipart/related when sending inline images
                    email_message = EmailMultiRelated(**kwargs)

                    # Put image content for attachments in *email_message*
                    attachments = EmailAttachment.objects.filter(pk__in=mapped_attachments.keys())
                    for attachment in attachments:
                        storage_file = default_storage._open(attachment.attachment.name)
                        filename = get_attachment_filename_from_url(attachment.attachment.name)

                        # Add as inline attachment
                        storage_file.open()
                        content = storage_file.read()
                        storage_file.close()
                        email_message.attach_related(filename, content, storage_file.key.content_type)

                        # Update attribute src for inline image with the Content-ID
                        inline_image = mapped_attachments[attachment.pk]
                        inline_image['src'] = 'cid:%s' % filename

                    # Use new HTML
                    email_message.attach_alternative(unsaved_form.body_html, 'text/html')

                success = True
                if 'submit-save' in self.request.POST:  # Save draft
                    success = self.save_message(account, server, email_message)
                elif 'submit-send' in self.request.POST:  # Send draft
                    if self.object:
                        email_message = self.attach_stored_files(email_message, self.object.pk)
                    success = self.send_message(account, server, email_message)
                    if success:
                        recipients = ', '.join(email_message.to + email_message.cc + email_message.bcc)
                        messages.success(self.request, _('E-mail sent to %s') % truncatechars(recipients, 140))

                # Remove an old draft when sending an e-mail message or saving a new draft
                if self.object and success and self.remove_old_message:
                    self.remove_draft(server)

            if 'submit-discard' in self.request.POST and self.object and self.remove_old_message:
                self.remove_draft(server)
        except Exception, e:
            log.error(traceback.format_exc(e))
        finally:
            if server:
                server.logout()

        return super(EmailMessageComposeBaseView, self).form_valid(form)

    def attach_request_files(self, email_message):
        """
        Attach files from request.FILES to *email_message* as separte mime parts.
        """
        attachments = self.request.FILES
        if len(attachments) > 0:
            for key, attachment in attachments.items():
                filetype = attachment.content_type.split('/')
                part = MIMEBase(filetype[0], filetype[1])
                part.set_payload(attachment.read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attachment.name))

                email_message.attach(part)

        return email_message

    def attach_stored_files(self, email_message, pk):
        """
        Attach EmailAttachments to *email_message* as separte mime parts.
        """
        attachments = EmailAttachment.objects.filter(inline=False, message_id=pk).all()
        if len(attachments) > 0:
            for attachment in attachments:
                storage_file = default_storage._open(attachment.attachment.name)
                filename = get_attachment_filename_from_url(attachment.attachment.name)

                storage_file.open()
                content = storage_file.read()
                storage_file.close()

                filetype = storage_file.key.content_type.split('/')
                part = MIMEBase(filetype[0], filetype[1])
                part.set_payload(content)
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(filename))

                email_message.attach(part)

        return email_message

    def save_message(self, account, server, email_message):
        """
        Save the message as a draft to the database and to the server via IMAP.
        """
        # Check for attachments
        email_message = self.attach_request_files(email_message)
        if self.object and self.object.pk:
            email_message = self.attach_stored_files(email_message, self.object.pk)

        message_string = email_message.message().as_string(unixfrom=False)
        try:
            # Save *email_message* as draft
            folder = server.get_folder(DRAFTS)

            # Save draft remotely
            response = server.client.append(folder.name_on_server,
                                            message_string,
                                            flags=[DRAFT])

            # Extract uid from response
            command, seq, uid, status = [part.strip('[]()') for part in response.split(' ')]
            uid = int(uid)

            # Sync this specific message
            message = server.get_message(
                uid,
                modifiers=['BODY.PEEK[]', 'FLAGS', 'RFC822.SIZE'],
                folder=folder
            )
            save_email_messages(
                [message],
                account,
                folder,
                new_messages=True
            )
            self.new_draft = EmailMessage.objects.get(
                account=account,
                uid=uid,
                folder_name=folder.name_on_server
            )
        except Exception, e:
            log.error(traceback.format_exc(e))
            return False

        return True

    def send_message(self, account, active_server, email_message):
        """
        Send the message via SMTP and save the sent message to the database.

        :param server: The server on which the message needs to be sent.
        :param email_message: The message that needs to be sent.
        :return: A Boolean indicating whether the save was successful.
        """
        # Check for attachments
        email_message = self.attach_request_files(email_message)

        try:
            # Send initial message
            connection = smtp_connect(account, fail_silently=False)
            connection.send_messages([email_message])

            # Send extra for BCC recipients if any
            if email_message.bcc:
                recipients = email_message.bcc

                # Send separate messages
                for recipient in recipients:
                    email_message.bcc = []
                    email_message.to = [recipient]
                    connection.send_messages([email_message])

            # Synchronize only new messages from folder *SENT*
            synchronize_folder(
                account,
                active_server,
                active_server.get_folder(SENT),
                criteria=['subject "%s"' % email_message.subject],
                new_only=True
            )
        except Exception, e:
            log.error(traceback.format_exc(e))
            return False

        return True

    def remove_draft(self, server):
        """
        Remove old version of the message from the server and the database.

        :param server: The server from which the old message needs to be removed.
        """
        if self.object and self.object.uid:
            folder = server.get_folder(DRAFTS)
            is_selected, select_info = server.select_folder(folder.get_search_name(), readonly=False)
            if is_selected:
                server.client.delete_messages([self.object.uid])
                server.client.close_folder()

        # Delete local attachments
        self.object.attachments.all().delete()
        self.object.delete()

    def get_email_headers(self):
        """
        This function is not implemented. For custom headers overwrite this function.
        """
        pass

    def get_context_data(self, **kwargs):
        """
        Get context data that is used for the rendering of the template.

        :param kwargs: Keyword arguments.
        :return: A dict containing the context data.
        """
        context = super(EmailMessageComposeBaseView, self).get_context_data(**kwargs)

        # Query for all contacts which have e-mail addresses
        contacts_addresses_qs = Contact.objects.filter(
            email_addresses__in=EmailAddress.objects.all()
        ).prefetch_related('email_addresses')

        known_contact_addresses = []
        for contact in contacts_addresses_qs:
            for email_address in contact.email_addresses.all():
                contact_address = u'"%s" <%s>' % (contact.full_name(), email_address.email_address)
                known_contact_addresses.append(contact_address)

        context.update({
            'known_contact_addresses': simplejson.dumps(known_contact_addresses),
        })

        # find e-mail templates and add to context in json
        templates = EmailTemplate.objects.all()
        template_list = {}
        for template in templates:
            template_list.update({
                template.pk: {
                    'subject': template.subject,
                    'html_part': TemplateParser(template.body_html).render(self.request),
                }
            })

        # only add template_list to context if there are any templates
        if template_list:
            context.update({
                'template_list': simplejson.dumps(template_list),
            })

        return context

    def get_success_url(self):
        """
        Return the appropriate success URL depending on the button pressed.

        :return: A success URL.
        """
        if 'submit-save' in self.request.POST:
            return reverse('messaging_email_compose', kwargs={'pk': self.new_draft.pk})
        elif 'submit-send' in self.request.POST:
            return reverse('messaging_email_inbox')
        else:
            return reverse('messaging_email_inbox')


class EmailMessageCreateView(EmailMessageComposeBaseView):
    remove_old_message = True
    message_object_query_args = (
        Q(folder_identifier=DRAFTS) |
        Q(flags__icontains='draft'))
email_create_view = login_required(EmailMessageCreateView.as_view())


class EmailMessageReplyView(EmailMessageComposeBaseView):
    remove_old_message = False
    message_object_query_args = (
        ~Q(folder_identifier=DRAFTS) &
        ~Q(flags__icontains='draft'))

    def get_form_kwargs(self, **kwargs):
        kwargs = super(EmailMessageReplyView, self).get_form_kwargs(**kwargs)

        kwargs['message_type'] = 'reply'

        if self.object:
            kwargs['initial']['subject'] = 'Re: %s' % self.object.subject
            kwargs['initial']['send_from'] = self.object.to_email
            kwargs['initial']['send_to_normal'] = self.object.from_combined

        return kwargs

    def get_email_headers(self):
        """
        Return reply-to e-mail header.
        """
        email_headers = {}
        if self.object and self.object.from_email:
            sender = email.utils.parseaddr(self.object.from_email)
            reply_to_name = sender[0]
            reply_to_address = sender[1]
            email_headers.update({'Reply-To': '"%s" <%s>' % (reply_to_name, reply_to_address)})
        return email_headers
email_reply_view = login_required(EmailMessageReplyView.as_view())


class EmailMessageForwardView(EmailMessageReplyView):
    remove_old_message = False
    message_object_query_args = (
        ~Q(folder_identifier=DRAFTS.lstrip('\\')) &
        ~Q(flags__icontains='draft'))

    def get_form_kwargs(self, **kwargs):
        """
        Get the keyword arguments that will be used to initiate the form.

        :return: A dict of keyword arguments.
        """
        kwargs = super(EmailMessageForwardView, self).get_form_kwargs(**kwargs)

        kwargs['message_type'] = 'forward'

        if self.object:
            kwargs['initial']['subject'] = 'Fwd: %s' % self.object.subject
            kwargs['initial']['send_from'] = self.object.to_email
            kwargs['initial']['send_to_normal'] = ''

        return kwargs

    def get_email_headers(self):
        """
        Return reply-to e-mail header.
        """
        email_headers = {}
        if self.object and self.object.to_email:
            sender = email.utils.parseaddr(self.object.to_email)
            reply_to_name = sender[0]
            reply_to_address = sender[1]
            email_headers.update({'Reply-To': '"%s" <%s>' % (reply_to_name, reply_to_address)})
        return email_headers
email_forward_view = login_required(EmailMessageForwardView.as_view())


class EmailBodyPreviewView(TemplateView):
    template_name = 'messaging/email/mwsadmin/email_compose_frame.html'  # default for non-templated e-mails

    def dispatch(self, request, *args, **kwargs):
        self.object_id = kwargs.get('object_id', None)
        self.message_type = kwargs.get('message_type', None)
        self.template_id = kwargs.get('template_id', None)
        self.message = None

        if self.message_type == 'template' and self.object_id:
            self.template = get_object_or_404(
                EmailTemplate,
                pk=self.object_id
            )
        elif self.object_id:
            self.message = get_object_or_404(
                EmailMessage,
                pk=self.object_id
            )

            if self.template_id:
                self.template = get_object_or_404(
                    EmailTemplate,
                    pk=self.template_id
                )

        return super(EmailBodyPreviewView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super(EmailBodyPreviewView, self).get_context_data(**kwargs)

        if self.message_type == 'template' and self.object_id:
            body = self.template.body_html
        elif self.message_type == 'new':
            if self.message is None:
                body = u''
            else:
                body = self.message.body_html or self.message.htmlify() or None
                if body is None:
                    server, self.message = self.get_message_from_imap(self.message)
                    self.message.save()
                    body = self.message.body_html or self.message.htmlify() or u''
        elif self.object_id:
            quoted_content = self.message.indented_body

            notice = None
            if self.message_type == 'forward':
                notice = _('Begin forwarded message:')
            elif self.message_type == 'reply':
                notice = _('On %s, %s wrote:' % (
                    self.message.sent_date.strftime(_('%b %e, %Y, at %H:%M')),
                    self.message.from_combined)
                )

            if notice is not None:
                quoted_content = '<div>' + notice + '</div>' + quoted_content

            if hasattr(self, 'template'):
                template = TemplateParser(self.template.body_html).render(self.request) or self.template.body_text
                body = '<div>' + template + '</div>' + '<br />' * 2 + quoted_content
            else:
                signature = u''
                body = signature + '<br />' * 2 + quoted_content
        else:
            body = u''

        kwargs.update({
            'draft': body
        })

        return kwargs

    def get_message_from_imap(self, instance):
        """
        Retrieve an e-mail via IMAP

        :param instance: the instance of a message
        :param pk: the primary key of a message
        :return: server used for connecting and the new updated instance
        """
        imap_logger.info('Connecting with IMAP')

        pk = instance.pk
        host = instance.account.provider.imap_host
        port = instance.account.provider.imap_port
        ssl = instance.account.provider.imap_ssl
        server = IMAP(host, port, ssl)
        server.login(instance.account.username, instance.account.password)

        imap_logger.info('Searching IMAP for %s in %s' % (instance.uid, instance.folder_name))

        message = server.get_message(instance.uid, ['BODY[]', 'FLAGS', 'RFC822.SIZE', 'INTERNALDATE'],
                                     server.get_folder(instance.folder_name), readonly=False)
        if message is not None:
            imap_logger.info('Message retrieved, saving in database')
            save_email_messages([message], instance.account, message.folder)

        instance = EmailMessage.objects.get(pk=pk)

        return server, instance
email_body_preview_view = login_required(EmailBodyPreviewView.as_view())


class EmailAttachmentProxy(View):
    def get(request, *args, **kwargs):
        pk = kwargs.get('pk')

        try:
            attachment = EmailAttachment.objects.get(pk=pk)
        except:
            raise Http404()

        s3_file = default_storage._open(attachment.attachment.name)

        wrapper = FileWrapper(s3_file)
        response = HttpResponse(wrapper, content_type='%s' % s3_file.key.content_type)
        response['Content-Disposition'] = 'attachment; filename=%s' % get_attachment_filename_from_url(s3_file.name)
        response['Content-Length'] = attachment.size
        return response
email_attachment_proxy_view = login_required(EmailAttachmentProxy.as_view())


class EmailConfigurationWizardView(SessionWizardView):
    template_name = 'email/emailaccount_configuration_wizard_form.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.email_address = EmailAddress.objects.get(pk=kwargs.get('pk'))
        except EmailAddress.DoesNotExist:
            raise Http404()

        return super(EmailConfigurationWizardView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self, step=None):
        """
        Returns the keyword arguments for instantiating the form
        (or formset) on the given step.
        """
        kwargs = super(EmailConfigurationWizardView, self).get_form_kwargs(step)

        # Provide form EmailConfigurationWizard_2 with the username/password
        # necessary to test the connection with the server details asked in
        # this form.
        if int(step) == 1:
            cleaned_data = self.get_cleaned_data_for_step(unicode(int(step) - 1))
            if cleaned_data is not None:
                kwargs.update({
                    'username': cleaned_data.get('username'),
                    'password': cleaned_data.get('password'),
                })

        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super(EmailConfigurationWizardView, self).get_context_data(form, **kwargs)
        context.update({
           'email_address': self.email_address,
        })
        return context

    def render(self, form=None, **kwargs):
        """
        Return a different response to ajax requests.
        """
        form = form or self.get_form()
        response = self.render_to_response(self.get_context_data(form=form, **kwargs))
        if is_ajax(self.request) and self.request.method.lower() == 'post':
            response = simplejson.dumps({
                'error': True,
                'html': response.rendered_content
            })
            return HttpResponse(response, mimetype='application/json')

        return response

    def done(self, form_list, **kwargs):
        data = {}

        for form in self.form_list.keys():
            data[form] = self.get_cleaned_data_for_step(form)

        # Save provider and emailaccount instances
        provider = EmailProvider()
        provider.__dict__.update(data['1'])
        # provider.imap_host = data['1']['imap_host']
        # provider.imap_port = data['1']['imap_port']
        # provider.imap_ssl = data['1']['imap_ssl']
        # provider.smtp_host = data['1']['smtp_host']
        # provider.smtp_port = data['1']['smtp_port']
        # provider.smtp_ssl = data['1']['smtp_ssl']

        provider.save()

        try:
            account = EmailAccount.objects.get(email=self.email_address)
        except EmailAccount.DoesNotExist:
            account = EmailAccount()
            account.email = self.email_address

        account.account_type = 'email'
        account.from_name = data['2']['name']
        #account.signature = data['2']['signature']
        account.signature = None
        account.username = data['0']['username']
        account.password = data['0']['password']
        account.provider = provider
        account.last_sync_date = datetime.datetime.now(tzutc()) - datetime.timedelta(days=1)
        account.auth_ok = OK_EMAILACCOUNT_AUTH
        account.save()

        # Authorize current user to emailaccount
        account.user_group.add(get_current_user())

        messages.success(self.request, _('Email address %s has been configured successfully.') % self.email_address.email_address)

        response = render_to_response('email/emailaccount_configuration_wizard_done.html', {
            'form_data': [form.cleaned_data for form in form_list],
        })
        if is_ajax(self.request):
            response = simplejson.dumps({
                'error': False,
                'html': response.content
            })
            return HttpResponse(response, mimetype='application/json')

        return response

email_configuration_wizard = login_required(EmailConfigurationWizardView.as_view([
    EmailConfigurationWizard_1,
    EmailConfigurationWizard_2,
    EmailConfigurationWizard_3
]))


# class EmailConfigurationWizardTemplate(TemplateView):
#     """
#     View to provide html for wizard form skeleton to configure e-mail accounts.
#     """
#     template_name = 'email/emailaccount_configuration_ajax.html'

# class EmailConfigurationView(SessionWizardView):
#     template_name = 'messaging/email/mwsadmin/wizard_configuration_form_step.html'

#     def dispatch(self, request, *args, **kwargs):
#         # Verify email address exists
#         self.email_address_id = kwargs.get('pk')
#         try:
#             self.email_address = EmailAddress.objects.get(pk=self.email_address_id)
#         except EmailAddress.DoesNotExist:
#             raise Http404()

#         # Set up initial values per step
#         self.initial_dict = {
#             '0': {},
#             '1': {},
#             '2': {}
#         }

#         # Default: email as username
#         self.initial_dict['0']['email'] = self.initial_dict['0']['username'] = self.email_address.email_address

#         try:
#             email_account = EmailAccount.objects.get(email=self.email_address)
#         except EmailAccount.DoesNotExist:
#             # Set from_name
#             contacts = self.email_address.contact_set.all()
#             if len(contacts) > 0:  # check to be safe, but should always have a contact when using this format
#                 contact = contacts[0]
#                 self.initial_dict['2']['name'] = contact.full_name()
#         else:
#             # Set provider data
#             self.initial_dict['1']['imap_host'] = email_account.provider.imap_host
#             self.initial_dict['1']['imap_port'] = email_account.provider.imap_port
#             self.initial_dict['1']['imap_ssl'] = email_account.provider.imap_ssl
#             self.initial_dict['1']['smtp_host'] = email_account.provider.smtp_host
#             self.initial_dict['1']['smtp_port'] = email_account.provider.smtp_port
#             self.initial_dict['1']['smtp_ssl'] = email_account.provider.smtp_ssl

#             # Set from_name and signature
#             self.initial_dict['2']['name'] = email_account.from_name
#             self.initial_dict['2']['signature'] = email_account.signature

#         return super(EmailConfigurationView, self).dispatch(request, *args, **kwargs)

#     def get(self, *args, **kwargs):
#         """
#         Reset storage on first request.
#         """
#         self.storage.reset()
#         return super(EmailConfigurationView, self).get(*args, **kwargs)

#     def post(self, *args, **kwargs):
#         """
#         Override POST to validate the form first.
#         """
#         # Get the form for the current step
#         form = self.get_form(data=self.request.POST.copy())

#         # On first request, there's nothing to validate
#         if self.storage.current_step is None:
#             # Render the same form if it's not valid, continue otherwise
#             if form.is_valid():
#                 return super(EmailConfigurationView, self).post(*args, **kwargs)
#             return self.render(form)
#         elif form.is_valid():
#             self.storage.set_step_data(self.steps.current, self.process_step(form))
#         else:
#             return self.render(form)
#         return super(EmailConfigurationView, self).post(*args, **kwargs)

#     def get_form_kwargs(self, step=None):
#         """
#         Returns the keyword arguments for instantiating the form
#         (or formset) on the given step.
#         """
#         kwargs = super(EmailConfigurationView, self).get_form_kwargs(step)

#         if int(step) == 1:
#             cleaned_data = self.get_cleaned_data_for_step(unicode(int(step) - 1))
#             if cleaned_data is not None:
#                 kwargs.update({
#                     'username': cleaned_data.get('username'),
#                     'password': cleaned_data.get('password'),
#                 })

#         return kwargs

#     def done(self, form_list, **kwargs):
#         data = {}
#         for form in self.form_list.keys():
#             data[form] = self.get_cleaned_data_for_step(form)

#         # Save provider and emailaccount instances
#         provider = EmailProvider()
#         provider.imap_host = data['1']['imap_host']
#         provider.imap_port = data['1']['imap_port']
#         provider.imap_ssl = data['1']['imap_ssl']
#         provider.smtp_host = data['1']['smtp_host']
#         provider.smtp_port = data['1']['smtp_port']
#         provider.smtp_ssl = data['1']['smtp_ssl']

#         provider.save()

#         try:
#             account = EmailAccount.objects.get(email=self.email_address)
#         except EmailAccount.DoesNotExist:
#             account = EmailAccount()
#             account.email = self.email_address

#         account.account_type = 'email'
#         account.from_name = data['2']['name']
#         account.signature = data['2']['signature']
#         account.username = data['0']['username']
#         account.password = data['0']['password']
#         account.provider = provider
#         account.last_sync_date = datetime.datetime.now(tzutc()) - datetime.timedelta(days=1)
#         account.save()

#         # Link contact's user to emailaccount
#         account.user_group.add(get_current_user())

#         return HttpResponse(render_to_string(self.template_name, {'messaging_email_inbox': reverse('messaging_email_inbox')}, None))
# email_configuration_wizard = login_required(EmailConfigurationView.as_view([EmailConfigurationStep1Form, EmailConfigurationStep2Form, EmailConfigurationStep3Form]))

class EmailShareView(FormView):
    """
    Display a form to share an email account with everybody or certain people only.
    """
    template_name = 'email/emailaccount_share_ajax.html'
    form_class = EmailShareForm

    def dispatch(self, request, *args, **kwargs):
        # Verify email address exists
        email_address_id = kwargs.get('pk')
        try:
            self.email_address = EmailAddress.objects.get(pk=email_address_id)
        except EmailAddress.DoesNotExist:
            raise Http404()

        # Verify email account exists
        try:
            self.email_account = EmailAccount.objects.get(email=self.email_address)
        except EmailAccount.DoesNotExist:
            raise Http404()

        return super(EmailShareView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self, **kwargs):
        original_user = None
        try:
            original_user = CustomUser.objects.get(tenant=get_current_user().tenant, contact__email_addresses__email_address=self.email_address, contact__email_addresses__is_primary=True)
        except CustomUser.DoesNotExist:
            pass

        kwargs = super(EmailShareView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            'instance': self.email_account,
            'original_user': original_user
        })

        return kwargs

    def form_valid(self, form):
        """
        Handle form submission via AJAX or show custom save message.
        """
        self.object = form.save()  # copied from ModelFormMixin

        # Show save message
        messages.success(self.request, _('Sharing options saved for:<br /> %s') % self.object.email.email_address)

        if is_ajax(self.request):
            # Return response
            return HttpResponse(simplejson.dumps({
                'error': False,
            }), mimetype='application/json')

        return super(EmailShareView, self).form_valid(form)

    def form_invalid(self, form):
        response = self.render_to_response(self.get_context_data(form=form))
        if is_ajax(self.request):
            response = simplejson.dumps({
                'error': True,
                'html': response.rendered_content
            })
            return HttpResponse(response, mimetype='application/json')

        return response

        return super(EmailShareView, self).form_invalid(form)
email_share_wizard = login_required(EmailShareView.as_view())


class EmailSearchView(EmailFolderView):
    def get(self, request, *args, **kwargs):
        """
        Parse search keys and search via IMAP.
        """
        # Look in url which account id and folder the searched is performed in
        account_id = kwargs.get('account_id', None)

        # Get accounts the user has access to
        if account_id is not None:
            accounts = [int(account_id)]
            accounts_qs = request.user.get_messages_accounts(EmailAccount, pk__in=accounts)

            if len(accounts_qs) == 0:  # when provided, but no matches were found raise 404
                raise Http404()
        else:
            accounts_qs = request.user.get_messages_accounts(EmailAccount)

        # Get folder name from url or settle for ALLMAIL
        folder_name = kwargs.get('folder', None)
        if folder_name is not None:
            self.folder = urllib.unquote_plus(folder_name)
            self.folder_locale_name = self.folder.split('/')[-1:][0]
            self.folder_name = self.folder_locale_name
            self.folder_identifier = None
        else:
            self.folder = self.folder_locale_name = ALLMAIL
            self.folder_identifier = ALLMAIL

        if len(set([INBOX, SENT, DRAFTS, TRASH, SPAM]).intersection(set([self.folder]))) > 0:
            folder_flag = set([INBOX, SENT, DRAFTS, TRASH, SPAM]).intersection(set([self.folder])).pop()
            self.folder_name = None
            self.folder_locale_name = None
            self.folder_identifier = folder_flag

        # Check if folder is from account
        folder_found = False
        for account in accounts_qs:
            for folder_name, folder in account.folders.items():
                if self.folder_identifier in folder.get('flags'):
                    folder_found = True
                    self.folder_locale_name = folder_name
                    break

                if folder_name == self.folder_locale_name:
                    folder_found = True
                    break

                if self.folder_identifier is not None:
                    if folder_name == self.folder_identifier.lstrip('\\'):
                        folder_found = True
                        self.folder_locale_name = folder_name
                        break

                children = folder.get('children', {})
                for sub_folder_name, sub_folder in children.items():
                    if self.folder_identifier in sub_folder.get('flags'):
                        folder_found = True
                        self.folder_locale_name = sub_folder_name
                        break

                    if sub_folder_name == self.folder_locale_name:
                        folder_found = True
                        break

                    if self.folder_identifier is not None:
                        if sub_folder_name == self.folder_identifier.lstrip('\\'):
                            folder_found = True
                            self.folder_locale_name = sub_folder_name
                            break

            if not folder_found:
                raise Http404()

        # Scrape messages together from one or more e-mail accounts
        search_criteria = parse_search_keys(kwargs.get('search_key'))
        self.imap_search_in_accounts(search_criteria, accounts=accounts_qs)

        return super(EmailSearchView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Check if we have something to search for
        if not request.POST.get('search_key'):
            return redirect(request.META.get('HTTP_REFERER'))

        # Redirect so self with the keyword in the url
        return redirect('%s%s/' % (request.path, request.POST.get('search_key')))

    def imap_search_in_accounts(self, search_criteria, accounts):
        """
        Perform a search on given or all accounts and save the results.
        """
        def get_uids_from_local(uids, account):
            qs = EmailMessage.objects.none()
            if self.folder_name is not None and self.folder_identifier is not None:
                qs = EmailMessage.objects.filter(Q(folder_identifier=self.folder_identifier) | Q(folder_name=self.folder_name))
            elif self.folder_name is not None:
                qs = EmailMessage.objects.filter(folder_name__in=[self.folder_name, self.folder])
            elif self.folder_identifier is not None:
                qs = EmailMessage.objects.filter(folder_identifier=self.folder_identifier)
            return qs.filter(account=account, uid__in=uids).order_by('-sent_date')

        self.resultset = []  # result set of email messages pks

        # Find corresponding messages in database and save message pks
        for account in accounts:
            server = None
            try:
                host = account.provider.imap_host
                port = account.provider.imap_port
                ssl = account.provider.imap_ssl
                server = IMAP(host, port, ssl)
                server.login(account.username,  account.password)

                folder = server.get_folder(self.folder_identifier or self.folder)
                total_count, uids = server.get_uids(folder, search_criteria)

                if len(uids):
                    qs = get_uids_from_local(uids, account)
                    if len(qs) == 0:
                        # Get actual messages for *uids* from *server* when they're not available locally
                        modifiers = ['BODY.PEEK[HEADER.FIELDS (Reply-To Subject Content-Type To Cc Bcc Delivered-To From Message-ID Sender In-Reply-To Received Date)]', 'FLAGS', 'RFC822.SIZE', 'INTERNALDATE']
                        folder_messages = server.get_messages(uids, modifiers, folder)

                        if len(folder_messages) > 0:
                            save_email_messages(folder_messages, account, folder, new_messages=True)

                    pks = qs.values_list('pk', flat=True)
                    self.resultset += list(pks)
            finally:
                if server:
                    server.logout()

    def get_queryset(self):
        """
        Return all messages matching the result set.
        """
        return EmailMessage.objects.filter(pk__in=self.resultset).extra(select={
            'num_attachments': 'SELECT COUNT(*) FROM email_emailattachment WHERE email_emailattachment.message_id = email_emailmessage.message_ptr_id AND inline=False'

        }).order_by('-sent_date')

    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to reflect the folder being searched in.
        """
        kwargs = super(EmailSearchView, self).get_context_data(**kwargs)
        kwargs.update({
            'list_title': _('%s for %s') % (self.folder_locale_name, kwargs.get('list_title')),
            'search_key': self.kwargs.get('search_key', ''),
        })
        return kwargs
email_search_view = login_required(EmailSearchView.as_view())
