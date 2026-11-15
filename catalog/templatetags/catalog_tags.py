from django import template

register = template.Library()


@register.filter
def get_attr(obj, attr):
    """Get an attribute from an object in a template."""
    if obj is None:
        return ''
    try:
        return getattr(obj, attr)
    except (AttributeError, TypeError):
        return ''


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary in a template."""
    if dictionary is None:
        return None
    try:
        return dictionary.get(key)
    except AttributeError:
        return None
