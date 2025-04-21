from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary by key
    Usage: {{ mydict|get_item:mykey }}
    """
    return dictionary.get(int(key))