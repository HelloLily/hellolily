"""
This file contains multiple new layout objects for django-app crispy-forms.
"""
from crispy_forms.layout import Div, HTML, MultiField, Button, ButtonHolder
from crispy_forms.utils import render_field
from django.conf import settings
from django.template.context import Context
from django.template.loader import render_to_string


class Anchor(HTML):
    """ 
    Crispy forms layout object. Add an anchor via the HTML class. 
    """
    def __init__(self, href='', text='', title='', css_id='', css_class=''):
        html = '<a href="%s" id="%s" class="%s" title="%s">%s</a>' % (href, css_id, css_class, title, text)
        super(Anchor, self).__init__(html)


class Column(Div):
    """
    Copy of the original Crispy forms layout object 'Column' but with more options for more
    detailed html.
    """
    css_class = 'mws-form-col-4-8'
    
    def __init__(self, *fields, **kwargs):
        size = kwargs.pop('size', 4)
        first = kwargs.pop('first', False)
        css_class = kwargs.pop('css_class', '')
        if size > 0 and size < 9:
            self.css_class = 'mws-form-col-%s-8' % size
            self.css_class += ' %s' % css_class
        if first:
            self.css_class += ' alpha'
        super(Column, self).__init__(*fields, **kwargs)
            

class Row(Div):
    """ 
    Wrap multiple fields in a single form row.
    """
    css_class = 'mws-form-row'


class InlineRow(Div):
    """ 
    Wrap multiple fields in a single form row.
    """
    css_class = 'mws-form-item'


class ColumnedRow(Div):
    """
    Wrapper for columned rows.
    """
    css_class="mws-form-cols clearfix"


class FormMessage(HTML):
    """
    Wrapper for form messages.
    """
    def __init__(self, message):
        html = '<div class="mws-form-row mws-message-container"> \
                    <div class="mws-form-row mws-reset-message"> \
                        %s \
                    </div> \
                </div>' % message
        super(FormMessage, self).__init__(html)


class PasswordStrengthIndicator(HTML):
    """
    Contains an indicator of the strength of a password.
    """
    def __init__(self):
        html = '<div class="mws-form-row"><div class="password_checker"> \
                    <div id="password_strength" class="password_strength"></div> \
                </div> \
                <div id="password-text"></div></div>'
        super(PasswordStrengthIndicator, self).__init__(html)


class MultiField(MultiField):
    """
    Render multiple fields with custom templates.
    """
    template = 'mws-admin/layout/multifield.html'
    def render(self, form, form_style, context):
#        if form.errors:
#            self.css_class += " error"

        # We need to render fields using django-uni-form render_field so that MultiField can
        # hold other Layout objects inside itself
        fields_output = u''
        self.bound_fields = []
        for field in self.fields:
            fields_output += render_field(field, form, form_style, context, '%s/multifield.html' % settings.CRISPY_TEMPLATE_PACK, self.label_class, layout_object=self)

        return render_to_string(self.template, Context({'multifield': self, 'fields_output': fields_output}))


class Button(Button):
    """Overriding default template."""
    template = 'mws-admin/layout/baseinput.html'


class ButtonHolder(ButtonHolder):
    """Overriding default template."""
    template = 'mws-admin/layout/buttonholder.html'
