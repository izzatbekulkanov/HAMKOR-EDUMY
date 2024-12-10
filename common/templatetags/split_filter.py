from django import template

register = template.Library()

@register.filter
def split(value, delimiter=","):
    """
    Stringni belgilangan delimitr bo‘yicha ajratadi va ro‘yxat qaytaradi.
    """
    return value.split(delimiter)
