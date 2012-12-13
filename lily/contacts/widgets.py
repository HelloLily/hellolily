from django.forms.widgets import Select
from django.utils.encoding import force_unicode
from django.utils.html import escape, conditional_escape

from lily.contacts.models import Contact


class ContactAccountSelect(Select):
    """
    A select widget which contains the account id for this contact as a data attribute for the option element.
    """

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        if option_value in selected_choices:
            selected_html = u' selected="selected"'
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        
        account_data_html = ' data-account-id="%s"' 
        try:
            contact = Contact.objects.get(pk=option_value)
            account = contact.get_primary_function().account
            account_data_html = account_data_html % account.pk
        except:
            account_data_html = account_data_html % 0
        
        return u'<option value="%s"%s%s>%s</option>' % (
            escape(option_value), selected_html, account_data_html,
            conditional_escape(force_unicode(option_label)))