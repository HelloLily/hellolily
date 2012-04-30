from django.template import Library, Node, NodeList
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
            warnings.warn("The ifisajax templatetag require that a "
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

