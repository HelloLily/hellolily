from django import template
from django.contrib.messages import INFO, SUCCESS, WARNING, ERROR
register = template.Library()

from lily.utils.functions import uniquify


@register.filter(name='unique_messages')
def unique_messages(messages):
    """
    Uniquify the messages from Django Messages Framework.
    """
    # Uniquify messages
    messages_list = []
    for m in messages:
        messages_list.append(m.message)
    messages_list = uniquify(messages_list)
    
    # Rebuild messages node
    messages_unique = []
    for m in messages:
        try:
            index = messages_list.index(m.message)
            messages_unique.append(m)
            del messages_list[index]
        except ValueError:
            pass
    
    return messages_unique


@register.filter(name='message_css_tags')
def message_css_tags(messages):
    """
    Add CSS classes to the messages from Django Messages Framework.
    """
    # Map message levels to CSS classes
    tag_mapping = {
        INFO: 'info mws-ic-16 ic-exclamation',
        SUCCESS: 'success mws-ic-16 ic-accept',
        WARNING: 'warning mws-ic-16 ic-error',
        ERROR: 'error mws-ic-16 ic-cross'
    }
    
    # Set new 'css_class' attribute
    for m in messages:
        print m.level
        m.extra_tags = tag_mapping.get(m.level)
    
    return messages
                