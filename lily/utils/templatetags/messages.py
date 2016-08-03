from django import template
from ..functions import uniquify

register = template.Library()

# Map message levels to CSS classes
tag_mapping = {
    'info': 'info mws-ic-16 ic-exclamation',
    'success': 'success mws-ic-16 ic-accept',
    'warning': 'warning mws-ic-16 ic-error',
    'error': 'error mws-ic-16 ic-cross'
}


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
    # Set new 'css_class' attribute
    for m in messages:
        m.extra_tags = tag_mapping.get(m.tags)

    return messages
