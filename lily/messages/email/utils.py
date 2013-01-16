import re

from BeautifulSoup import BeautifulSoup, Comment
from django.db import models
from django.conf import settings
from django.template import Context, VARIABLE_TAG_START, VARIABLE_TAG_END, BLOCK_TAG_START, BLOCK_TAG_END
from django.template.loader import get_template_from_string
from django.template.loader_tags import BlockNode, ExtendsNode


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


def _parse_params(text):
    param_re = (re.compile('(%s[\s]*[\w]*[\s]*%s)' % (re.escape(VARIABLE_TAG_START), re.escape(VARIABLE_TAG_END))))

    # var list that filters variables that are not allowed
    #    var_list = [x.strip(' {}') for x in re.findall(var_re, text) if x.strip(' {}') in get_email_parameter_dict()]
    # var list that does not filter variables that are not allowed
    param_list = [x.strip(' {}') for x in re.findall(param_re, text)]

    return param_list


def _parse_blocks(text):
    block_re = (re.compile('(%s[\s]*[\w]*[\s]*%s)' % (re.escape(BLOCK_TAG_START), re.escape(BLOCK_TAG_END))))

    # block list that filters blocks that are not allowed
    #    block_list = [x.strip(' {%}') for x in re.findall(block_re, text) if x.strip(' {%}') in ['email_part', 'text_part']]
    # block list that does not filter blocks that are not allowed
    block_list = [x.strip(' {%}') for x in re.findall(block_re, text)]

    return block_list


def parse_parameters(text):
    """
    Parse given text and return all parameters that are supported.

    """
    return list(set(_parse_params(text)).intersection( set(get_email_parameter_dict()) ))


def parse_text(text, file=False):
    if file:
        # the method is called to parse a file so we need to check for a text_part and html_part
        pass
    else:
        # the method is called to parse a normal text so we only have to escape not supported blocks and parameters
        pass



    return {
        'html': 'html_part',
        'text': 'text_part',
    }


def get_param_vals(request, template):
    """
    Fill the parameters with actual values for rendering.

    """
    html_params = parse_parameters(template.html) if hasattr(template, 'html') else []
    text_params = parse_parameters(template.text) if hasattr(template, 'text') else []
    parsed_param_list = {}.fromkeys(html_params + text_params).keys()

    param_dict = get_email_parameter_dict()
    result_dict = {}
    filled_param_dict = {}

    # Get needed results from database
    for param in parsed_param_list:
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


def flatten_html_to_text(html):
    """
    Strip html and unwanted whitespace to preserve text only.
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
        linebreak.replaceWith(' ')

    if soup.body:
        flat_body = soup.body
    else:
        flat_body = soup

    # Strip tags and whitespace
    return ''.join(flat_body.findAll(text=True)).strip('&nbsp;\n ').replace('\r\n', ' ').replace('\r', '').replace('\n', ' ').replace('&nbsp;', ' ')  # pass html white-space to strip() also

    
class TemplateFileParser(object):
    """
    TODO
    """
    def __init__(self, file, context, parts=None):
        self.file = file
        self.content = self._make_safe(file.read())
        self.template = get_template_from_string(self.content)
        self.parts = parts or getattr(settings, 'EMAIL_TEMPLATE_FILE_PARTS', ['name', 'description', 'subject', 'html_part', 'text_part', ])
        self.context = context

    def parse(self):
        render_context = Context(self.context, autoescape=False)
        response = {}

        for part in self.parts:
            value = self._get_node(self.template, render_context, name=part).strip()

            if value:
                response[part] = value

        if not response:
            if self.file.content_type == 'text/html':
                response['html_part'] = self.content
            else:
                response['text_part'] = self.content

        return response

    def _make_safe(self, text):
        for parameter in self._get_parameter_list(text):
            stripped_parameter = parameter.strip(' {}')
            if not re.match("^[A-Za-z0-9_.]*$", stripped_parameter) or stripped_parameter not in get_email_parameter_dict():
                text = text.replace('%s' % parameter, '%s' % stripped_parameter)
            else:
                text = text.replace('%s' % parameter, '{%% templatetag openvariable %%} %s {%% templatetag closevariable %%}' % stripped_parameter)

        for block in self._get_block_list(text):
            pass

        return text

    def _get_parameter_list(self, text):
        param_re = (re.compile('(%s[\s]*.*[\s]*%s)' % (re.escape(VARIABLE_TAG_START), re.escape(VARIABLE_TAG_END))))

        return [x for x in re.findall(param_re, text)]

    def _get_block_list(self, text):
        block_re = (re.compile('(%s[\s]*.*[\s]*%s)' % (re.escape(BLOCK_TAG_START), re.escape(BLOCK_TAG_END))))

        return [x for x in re.findall(block_re, text)]

    def _get_node(self, template, context=Context(), name='subject', block_lookups={}):
        for node in template:
            if isinstance(node, BlockNode) and node.name == name:
                #Rudimentary handling of extended templates, for issue #3
                for i in xrange(len(node.nodelist)):
                    n = node.nodelist[i]
                    if isinstance(n, BlockNode) and n.name in block_lookups:
                        node.nodelist[i] = block_lookups[n.name]
                return node.render(context)
            elif isinstance(node, ExtendsNode):
                lookups = dict([(n.name, n) for n in node.nodelist if isinstance(n,BlockNode)])
                lookups.update(block_lookups)
                return self._get_node(node.get_parent(context), context, name, lookups)
        return ''


