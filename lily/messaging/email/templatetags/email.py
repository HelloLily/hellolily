from __future__ import absolute_import
from bs4 import BeautifulSoup
from collections import OrderedDict
import urllib
from datetime import datetime

from dateutil.tz import gettz, tzutc
from dateutil.parser import parse
from django import template
from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from lily.messaging.email.utils import INBOX, SENT, DRAFTS, TRASH, SPAM


register = template.Library()


def localized_times(time):
    if isinstance(time, basestring):
        parsed_time = parse(time)
        parsed_time.tzinfo._name = None  # clear tzname to rely solely on the offset (not all tznames are supported)
        utc_time = parsed_time.astimezone(tzutc())
    elif isinstance(time, datetime):
        utc_time = time.astimezone(tzutc())
    else:
        return None

    # Convert to local
    localized_time = utc_time.astimezone(gettz(settings.TIME_ZONE))
    localized_now = datetime.now(tzutc()).astimezone(gettz(settings.TIME_ZONE))
    return localized_time, localized_now


@register.filter(name='pretty_datetime')
def pretty_datetime(time, format=None):
    """
    Returns a string telling how long ago datetime differs from now or format
    it accordingly. Time is an UTC datetime.
    """
    # Convert to local
    localized_time, localized_now = localized_times(time)

    if isinstance(format, basestring):
        return datetime.strftime(localized_time, format)

    # Format based on local times
    if localized_now.toordinal() - localized_time.toordinal() == 0:  # same day
        return datetime.strftime(localized_time, '%H:%M')
    elif localized_now.year != localized_time.year:
        return datetime.strftime(localized_time, '%d-%m-%y')
    else:
        return datetime.strftime(localized_time, '%d-%b.')


@register.filter(name='pretty_datetime_relative')
def pretty_datetime_relative(time, format=None):
    result = pretty_datetime(time, format)

    # Convert to local
    localized_time, localized_now = localized_times(time)

    diff = localized_now - localized_time
    if diff.days > 14 or diff.days < 0:
        return result
    else:
        s = diff.seconds
        if diff.days > 1:
            return _('%s (%s days ago)') % (result, diff.days)
        elif diff.days == 1:
            if localized_now.toordinal() - localized_time.toordinal() == 1:
                return _('%s (yesterday)') % localized_time.strftime('%H:%M')
            else:
                return _('%s (2 days ago)') % result
        elif s <= 1:
            return _('%s (just now)') % result
        elif s < 60:
            return _('%s (%d seconds ago)') % (result, s)
        elif s < 120:
            return _('%s (1 minute ago)') % result
        elif s < 3600:
            return _('%s (%d minutes ago)') % (result, (s / 60))
        elif s < 7200:
            return _('1 hour ago')
        else:
            return _('%s (%d hours ago)') % (result, (s / 3600))


@register.filter(name='other_mailbox_folders')
def other_mailbox_folders(email_account, active_url):
    def filter_other_folders(folder_tree):
        other_folders = OrderedDict()
        for folder_name, folder in folder_tree.items():
            if not len(set([INBOX, SENT, DRAFTS, TRASH, SPAM]).intersection(set(folder.get('flags', [])))):
                other_folders[folder_name] = folder

        # Sort other mailbox folders
        other_folders_sorted = OrderedDict()
        for folder_name in sorted(other_folders, key=unicode.lower):
            other_folders_sorted[folder_name] = other_folders.get(folder_name)

        return other_folders_sorted

    def get_folder_html(folder_name, folder):
        folder_url = reverse('messaging_email_account_folder', kwargs={
            'account_id': email_account.id,
            'folder': urllib.quote_plus(folder.get('full_name').encode('utf-8'))
        })
        is_endpoint = is_active = urllib.unquote_plus(folder_url.encode('utf-8')) == urllib.unquote_plus(active_url)

        data_href = u'data-href="%(folder_url)s"' % {'folder_url': folder_url}
        html = u''
        if folder.get('is_parent', False):
            if u'\\Noselect' in folder.get('flags'):
                data_href = u''
            else:
                folder_name = u'''%(folder_name)s (%(unread_emails_count)s)''' % {
                    'folder_name': folder_name,
                }

            html += u'''<div class="tree-folder">
                            <div class="tree-folder-header %(tree_folder_class)s" %(data_href)s>
                                <i class="icon-folder-%(state)s"></i>
                                <div class="tree-folder-name">%(folder)s</div>
                            </div>
                            <div class="tree-folder-content %(folder_content_class)s" data-scroller="true"
                            data-max-height="256px" data-always-visible="1" data-rail-visible="0">'''

            is_folder_active, subfolder_html = get_subfolder_html(folder.get('children'))
            # Make sure parent is marked active as well
            if is_folder_active:
                is_active = True

            html %= {
                'tree_folder_class': 'tree-selected' if is_endpoint else '',
                'data_href': data_href,
                'state': 'open' if is_active else 'close',
                'folder': folder_name,
                'folder_content_class': '' if is_active else 'hide',
            }

            html += subfolder_html

            html += u'''</div>
                    </div>'''
        else:
            html += u'''<div class="tree-item %(tree_item_class)s" %(data_href)s>
                            <div class="tree-item-name">%(folder_name)s (%(unread_emails_count)s)</div>
                        </div>''' % {
                'tree_item_class': 'tree-selected' if is_endpoint else '',
                'data_href': data_href,
                'folder_name': folder_name,
            }

        return is_active, html

    def get_subfolder_html(folder_tree):
        other_folder_tree = filter_other_folders(folder_tree)

        html = u''
        is_active = False
        for folder_name, folder in other_folder_tree.items():
            is_folder_active, folder_html = get_folder_html(folder_name, folder)
            if is_folder_active:
                is_active = True

            html += folder_html

        return is_active, html

    # Find email_account's other mailbox folders
    other_folders = filter_other_folders(email_account.folders)

    # Generate output
    html = u''
    if len(other_folders):
        html += u'''<div class="tree-folder">
                        <div class="tree-folder-header">
                            <i class="icon-folder-%(state)s"></i>
                            <div class="tree-folder-name">%(folder_name)s</div>
                        </div>
                        <div class="tree-folder-content %(folder_content_class)s">'''

        # Loop through other mailbox folder trees
        folders_html = u''
        is_active = False
        for folder_name, folder in other_folders.items():
            is_folder_active, folder_html = get_folder_html(folder_name, folder)
            if is_folder_active:
                is_active = True
            folders_html += folder_html

        html %= {
            'state': 'open' if is_active else 'close',
            'folder_name': _('Other'),
            'folder_content_class': '' if is_active else 'hide',
        }

        html += folders_html

        html += u'''</div>
                </div>'''

    return html


@register.filter(name='replace_mailto')
def replace_mailto(value):
    '''
    Filter to replace mailto links with an url to compose new mail within Lily.
    '''
    soup = BeautifulSoup(value, 'lxml')
    mailto_tags = soup.select('a[href^=mailto]')

    for mailto_tag in mailto_tags:
        mailto_tag['href'] = mailto_tag['href'].replace("mailto:", "/#/email/compose/")
        mailto_tag['target'] = '_top'  # Break out of iframe.

    return str(soup)
