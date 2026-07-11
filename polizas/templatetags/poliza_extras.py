from django import template

register = template.Library()


@register.filter
def get_item(dic, key):
    if not dic:
        return 0
    try:
        return dic.get(key, 0) or 0
    except AttributeError:
        return 0
