import re

from BeautifulSoup import BeautifulSoup, Comment
from django.template import VARIABLE_TAG_END, VARIABLE_TAG_START
from django.db import models


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


def parse(text):
    """
    Parse given text and return all parameters that are in it.

    """
    tag_re = (re.compile('(%s.*?%s)' % (re.escape(VARIABLE_TAG_START), re.escape(VARIABLE_TAG_END))))
    parameter_list = []

    for bit in tag_re.split(text):
        if bit.startswith(VARIABLE_TAG_START) and bit.endswith(VARIABLE_TAG_END):
            parameter = bit[2:-2].strip()
            if parameter not in parameter_list and re.match("^[A-Za-z0-9_.]*$", parameter) and parameter in get_email_parameter_dict():
                parameter_list.append(parameter)

    return parameter_list


def get_param_vals(request, template):
    """
    Fill the parameters with actual values for rendering.

    """
    html_params = parse(template.html) if hasattr(template, 'html') else []
    text_params = parse(template.text) if hasattr(template, 'text') else []
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
    return ''.join(flat_body.findAll(text=True)).strip('&nbsp;\n ').replace('\r\n', ' ').replace('\r', '').replace('\n', ' ').replace('&nbsp;', ' ')  # pass html white-space to strip() also
