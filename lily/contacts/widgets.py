from itertools import chain

from django.forms.widgets import Select
from django.utils.encoding import force_unicode
from django.utils.html import escape, conditional_escape


class ContactAccountSelect(Select):
    """
    A select widget which contains the account id for this contact as a data attribute for the option element.
    """
    def __init__(self, contact_qs, attrs={}, choices=()):
        super(Select, self).__init__(attrs)

        contacts = contact_qs.prefetch_related('functions__account')
        self.choices = []
        for contact in contacts:
            account_id = 0
            if len(contact.functions.all()):
                account_id = contact.functions.all()[0].account_id
            self.choices.append((contact.id, account_id, unicode(contact)))

    def render_option(self, selected_choices, contact_id, account_id, option_label):
        contact_id = force_unicode(contact_id)
        if contact_id in selected_choices:
            selected_html = u' selected="selected"'
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(contact_id)
        else:
            selected_html = ''

        account_data_html = ' data-account-id="%s"' % account_id
        return u'<option value="%s"%s%s>%s</option>' % (
            escape(contact_id), selected_html, account_data_html,
            conditional_escape(force_unicode(option_label)))

    def render_options(self, choices, selected_choices):
        # Normalize to strings.
        selected_choices = set(force_unicode(v) for v in selected_choices)
        output = []
        for contact_id, account_id, contact_repr in chain(self.choices, choices):
            output.append(self.render_option(selected_choices, contact_id, account_id, contact_repr))
        return u'\n'.join(output)
