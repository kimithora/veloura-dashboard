from django import template

register = template.Library()


@register.filter
def get_attr(obj, attr):
    """Get an attribute from an object in a template. Supports dot-notation
    for related fields (e.g. 'customer.full_name', 'order.order_number')."""
    if obj is None:
        return ''
    try:
        value = obj
        for part in attr.split('.'):
            value = getattr(value, part)
            if value is None:
                return ''
        return value
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
