from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return '' 

@register.filter(name='divide')
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return ''

@register.filter(name='int_floor')
def int_floor(value):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0
    
@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)