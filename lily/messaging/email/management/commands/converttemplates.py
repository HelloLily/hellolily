import re
from django.core.management import BaseCommand

from ...models.models import EmailTemplate


class Command(BaseCommand):
    help = """
    Convert templates converts the closing and end tags of the email variables in a template to the given char(s).
    Can also be used to remove non-breaking spaces from a template.
    To use that function only submit the current_open_var and current_close_var.

    Args:
        current_open_var: The current char(s) to open the template variable with
        current_close_var: The current char(s) to close the template variable with
        open_var: The char(s) to open the template variable with
        close_var: The char(s) to close the template variable with
    """

    def handle(self, current_open_var, current_close_var, open_var='', close_var='', **kwargs):
        email_templates = EmailTemplate.objects.all()

        for email_template in email_templates:
            current_open_var_regex = ''
            current_close_var_regex = ''

            # Following code is to make sure the given vars are regex friendly
            for token in current_open_var:
                current_open_var_regex += '\\' + token

            for token in current_close_var:
                current_close_var_regex += '\\' + token

            variable_regex = current_open_var_regex + '&nbsp.+' + current_close_var_regex
            # Get all template variables that contain an &nbsp;
            nbsp_search_result = re.findall(variable_regex, email_template.body_html)

            if nbsp_search_result:
                for template_variable in nbsp_search_result:
                    # Change the nbsp to an actual space
                    replace_variable = template_variable.replace('&nbsp;', ' ')
                    # Replace the variable in the actual text
                    email_template.body_html = re.sub(variable_regex, replace_variable, email_template.body_html)

                email_template.save()
                print 'Removed non-breaking space (&nbsp;) from template ' + str(email_template.id) + ' (' + email_template.name + ')'

            if open_var and close_var:
                # Setup regex to find any characters between the two current delimiters
                search_regex = current_open_var_regex + '(.*?)' + current_close_var_regex
                # Find all occurences
                search_result = re.findall(search_regex, email_template.body_html)

                if search_result:
                    for template_variable in search_result:
                        find = current_open_var_regex + template_variable + current_close_var_regex
                        replace = open_var + template_variable + close_var

                        email_template.body_html = re.sub(find, replace, email_template.body_html, 1)

                    email_template.save()
                    print 'Converted template ' + str(email_template.id) + ' (' + email_template.name + ')'
                else:
                    print 'No results found for ' + str(email_template.id) + ' (' + email_template.name + ')'
