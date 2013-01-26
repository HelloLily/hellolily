import re

from BeautifulSoup import BeautifulSoup, Comment
from django.db import models
from django.template import Context, VARIABLE_TAG_START, VARIABLE_TAG_END, BLOCK_TAG_START, BLOCK_TAG_END, TemplateSyntaxError, TemplateDoesNotExist, TemplateEncodingError, VariableDoesNotExist, InvalidTemplateLibrary
from django.template.loader import get_template_from_string
from django.template.loader_tags import BlockNode, ExtendsNode
from lily.messaging.email.decorators import get_safe_template


_EMAIL_PARAMETER_DICT = {}
_EMAIL_PARAMETER_CHOICES = {}


def get_email_parameter_dict():
    """
    If there is no e-mail parameter dict yet, construct it and return it.
    The e-mail parameter dict consists of all posible variables for e-mail templates.

    This function returns parameters organized by variable name for easy parsing.

    """
    if not _EMAIL_PARAMETER_DICT:
        for model in models.get_models():
            if hasattr(model, 'email_template_parameters'):
                for field in model.email_template_parameters:
                    _EMAIL_PARAMETER_DICT.update({
                        '%s_%s' % (model._meta.verbose_name.lower(), field.name.lower()): {
                            'model': model,
                            'model_verbose': model._meta.verbose_name.title(),
                            'field': field,
                            'field_verbose': field.verbose_name.title(),
                        }
                    })
    return _EMAIL_PARAMETER_DICT


def get_email_parameter_choices():
    """
    If there is no e-mail parameter choices yet, construct it and return it.
    The e-mail parameter choices consists of all possible variables for e-mail templates.

    This function returns parameters organized by model name, for easy selecting.

    """
    if not _EMAIL_PARAMETER_CHOICES:
        for model in models.get_models():
            if hasattr(model, 'email_template_parameters'):
                for field in model.email_template_parameters:
                    if '%s' % model._meta.verbose_name.title() in _EMAIL_PARAMETER_CHOICES:
                        _EMAIL_PARAMETER_CHOICES.get('%s' % model._meta.verbose_name.title()).update({
                            '%s_%s' % (model._meta.verbose_name.lower(), field.name.lower()): field.verbose_name.title(),
                        })
                    else:
                        _EMAIL_PARAMETER_CHOICES.update({
                            '%s' % model._meta.verbose_name.title(): {
                                '%s_%s' % (model._meta.verbose_name.lower(), field.name.lower()): field.verbose_name.title(),
                            }
                        })

    return _EMAIL_PARAMETER_CHOICES


def flatten_html_to_text(html, replace_br=False):
    """
    Strip html and unwanted whitespace to preserve text only. Optionally replace
    <br> tags with line breaks (\n).
    """
    soup = BeautifulSoup(html)

    # Remove html comments
    comments = soup.findAll(text=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()

    # Remove several tags from flat_soup
    extract_tags = ['style', 'script', 'img', 'object', 'audio', 'video', 'doctype']
    for elem in soup.findAll(extract_tags):
        elem.extract()

    # Replace html line breaks with spaces to prevent lines appended after one another
    for linebreak in soup.findAll('br'):
        linebreak.replaceWith('\n' if replace_br else ' ')

    if soup.body:
        flat_body = soup.body
    else:
        flat_body = soup

    # Strip tags and whitespace
    return ''.join(flat_body.findAll(text=True)).strip('&nbsp;\n ').replace('\r\n', ' ').replace('\r', '').replace('\n', '\n' if replace_br else ' ').replace('&nbsp;', ' ')  # pass html white-space to strip() also


class TemplateParser(object):
    """
    Parse template input and provide helper functions for further template handling.
    """
    def __init__(self, text):
        self.valid_parameters = []
        self.valid_blocks = []
        text = self._escape_text(text).strip()

        safe_get_template_from_string = get_safe_template(get_template_from_string)

        try:
            self.template = safe_get_template_from_string(text)
            self.error = None
        except TemplateSyntaxError as error:
            self.template = None
            self.error = error

    def render(self, request, context=None):
        """
        Render the template in a form that is ready for output.
        """
        context = context or self.get_template_context(request)
        return get_template_from_string(self.get_text()).render(context=Context(context))

    def is_valid(self):
        """
        Return wheter the template is valid or not.
        """
        return self.template and not self.error

    def get_text(self):
        """
        Return the unrendered text, so variables etc. are still visible.
        """
        return self.template.render(context=Context())

    def get_parts(self, default_part='html_part', parts=None):
        """
        Return the contents of specified parts, if no parts are available return the default part.
        """
        parts = parts or ['name', 'description', 'subject', 'html_part', 'text_part', ]
        response = {}

        for part in parts:
            value = self._get_node(self.template, name=part).strip()

            if value:
                response[part] = value

        if not response:
            response[default_part] = self.get_text()

        return response

    def get_template_context(self, request):
        """
        Retrieve the context used for rendering of the template in a dict.
        """
        parameters = self.valid_parameters
        param_dict = get_email_parameter_dict()
        result_dict = {}
        filled_param_dict = {}

        # Get needed results from database
        for param in parameters:
            model = param_dict[param]['model']
            field = param_dict[param]['field']
            lookup = model.email_template_lookup

            if model not in result_dict:
                result_dict.update({
                    '%s' % model: eval(lookup)
                })

            filled_param_dict.update({
                '%s' % param: getattr(result_dict['%s' % model], field.name),
            })

        return filled_param_dict

    def get_parameter_list(self, text):
        """
        Retrieve all parameters using a regex.
        """
        param_re = (re.compile('(%s[\s]*.*[\s]*%s)' % (re.escape(VARIABLE_TAG_START), re.escape(VARIABLE_TAG_END))))

        return [x for x in re.findall(param_re, text)]

    def _escape_text(self, text):
        """
        Escape variables and delete django syntax around variables that are not allowed.
        """
        for parameter in self.get_parameter_list(text):
            stripped_parameter = parameter.strip(' {}')
            split_parameter = stripped_parameter.split('|')[0]
            if re.match("^[A-Za-z0-9_.]*$", split_parameter) and split_parameter in get_email_parameter_dict():
                # variable is accepted, now just escape so it can be rendered later
                text = text.replace('%s' % parameter, '{%% templatetag openvariable %%} %s {%% templatetag closevariable %%}' % stripped_parameter)
                self.valid_parameters.append(stripped_parameter)
            else:
                # variable is not accepted, remove surrounding braces
                text = text.replace('%s' % parameter, '%s' % stripped_parameter)

        return text

    def _get_node(self, template, context=Context(), name='subject', block_lookups=None):
        """
        Get contents of specified node out of the template.
        """
        block_lookups = block_lookups or {}
        for node in template:
            if isinstance(node, BlockNode) and node.name == name:
                #Rudimentary handling of extended templates, for issue #3
                for i in xrange(len(node.nodelist)):
                    n = node.nodelist[i]
                    if isinstance(n, BlockNode) and n.name in block_lookups:
                        node.nodelist[i] = block_lookups[n.name]
                return node.render(context)
            elif isinstance(node, ExtendsNode):
                lookups = dict([(n.name, n) for n in node.nodelist if isinstance(n, BlockNode)])
                lookups.update(block_lookups)
                return self._get_node(node.get_parent(context), context, name, lookups)
        return ''
