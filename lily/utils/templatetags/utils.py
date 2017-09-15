import re

from django.urls import reverse
from django.template import Library, Node, NodeList
from django.utils.encoding import force_unicode
from django.utils.http import int_to_base36, urlquote_plus
from django.utils.translation import ugettext_lazy as _
register = Library()


def parse_if_else(parser, token, end_tag):
    """
    Parse the contents within if/else/end tags and return
    two variables with the content between if/else or else/end tags.
    """
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()

    return nodelist_true, nodelist_false


class IsAjaxBase(Node):
    def __init__(self, nodelist_true, nodelist_false):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        request = context.get('request')

        # Gracefully fail if request is not in the context
        if not request:
            import warnings
            # TODO: django.core.context_processors.request and TEMPLATE_CONTEXT_PROCESSORS are removed in django 1.10
            warnings.warn(
                "The ifisajax templatetag require that a "
                "'request' variable is available in the template's "
                "context. Check you are using a RequestContext to "
                "render your template, and that "
                "'django.core.context_processors.request' is in "
                "your TEMPLATE_CONTEXT_PROCESSORS setting"
            )
            return self.nodelist_false.render(context)

        # Do the is_ajax check
        is_ajax = self.is_ajax(request)
        if is_ajax:
            # Return the content between if/else
            return self.nodelist_true.render(context)
        else:
            # Return the content between else/end
            return self.nodelist_false.render(context)


class IsAjaxNode(IsAjaxBase):
    def is_ajax(self, request):
        """
        Return True if the request is made via AJAX.
        """
        return request.is_ajax() or 'xhr' in request.GET


class IsNotAjaxNode(IsAjaxBase):
    def is_ajax(self, request):
        """
        Return True if the request is not made via AJAX.
        """
        return not request.is_ajax() and 'xhr' not in request.GET


@register.tag
def ifisajax(parser, token):
    nodelist_true, nodelist_false = parse_if_else(parser, token, 'endifisajax')
    return IsAjaxNode(nodelist_true, nodelist_false)


@register.tag
def ifnotisajax(parser, token):
    nodelist_true, nodelist_false = parse_if_else(parser, token, 'endifnotisajax')
    return IsNotAjaxNode(nodelist_true, nodelist_false)


@register.filter
def joinby(value, delimiter):
    """
    Simply create a string delimiter by given character.
    When a list with database items is given it will use the primary keys.
    """
    items = []
    if type(value) == list:
        for item in value:
            if item.pk:
                items.append(str(int_to_base36(item.pk)))
            else:
                item.append(item)
    else:
        items = value

    return delimiter.join(items)


@register.filter
def in_group(user, groups):
    """
    Returns a boolean if the user is in the given group, or comma-separated
    list of groups.

    Usage::

        {% if user|in_group:"Friends" %}
        ...
        {% endif %}

    or::

        {% if user|in_group:"Friends,Enemies" %}
        ...
        {% endif %}

    """
    group_list = force_unicode(groups).split(',')
    return bool(user.groups.filter(name__in=group_list).values('name'))


@register.filter
def classname(obj, arg=None):
    """
    Return the classname of given object or compare the classname to the given argument.
    """
    classname = obj.__class__.__name__.lower()
    if arg:
        if arg.lower() == classname:
            return True
        else:
            return False
    else:
        return classname


@register.filter
def priority(obj):
    """
    Return the appropriate css class for given priority.
    """
    css_classes = ['success', 'info', 'warning', 'danger']
    return css_classes[obj.priority]


@register.filter
def uri_detect(content):
    """
    Return given text with all uri's wrappped in html anchors. Adds 'http://' when missing protocol.
    """
    return re.sub(
        r'(([A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)',
        lambda match:
            '<a href="%s">%s</a>' %
            ('http://%s' % match.group(1) if match.group(1).find('http://') != 0 else match.group(1), match.group(1)),
        content)


@register.filter
def tags_to_uri(content):
    """
    For microblog: return given text with all hashtags wrapped in html anchors.
    """
    return re.sub(
        r'(^|\s|\S)(?<!&)#([^\s]+)',
        lambda match: '%s<a href="%s" title="%s">#%s</a>' %
                      (match.group(1), reverse('dashboard_tag',
                                               kwargs={'tag': urlquote_plus(match.group(2))}),
                       _('Show all posts with tag #%s') % match.group(2), match.group(2)),
        content)
