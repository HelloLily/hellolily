import re
from django.core.management import BaseCommand

from ...models.models import EmailTemplate


class Command(BaseCommand):
    help = """
    Convert templates converts the closing and end tags of the email variables in a template to the given char(s)

    Args:
        current_open_var: The current char(s) to open the template variable with
        current_close_var: The current char(s) to close the template variable with
        open_var: The char(s) to open the template variable with
        close_var: The char(s) to close the template variable with
    """

    def handle(self, current_open_var, current_close_var, open_var, close_var, **kwargs):
        email_templates = EmailTemplate.objects.all()

        for email_template in email_templates:
            current_open_var_regex = ''
            current_close_var_regex = ''

            # Following code is to make sure the given vars are regex friendly
            for token in current_open_var:
                current_open_var_regex += '\\' + token

            for token in current_close_var:
                current_close_var_regex += '\\' + token

            # Setup regex to find any characters between the two current delimiters
            search_regex = current_open_var_regex + '(.*?)' + current_close_var_regex
            # Find all occurences
            search_result = re.findall(search_regex, email_template.body_html)

            if search_result:
                template_variables = search_result

                for template_variable in template_variables:
                    find = current_open_var_regex + template_variable + current_close_var_regex
                    replace = open_var + template_variable + close_var

                    email_template.body_html = re.sub(find, replace, email_template.body_html, 1)

                email_template.save()
                print 'Converted template ' + email_template.name
            else:
                print 'No results found for ' + email_template.name
