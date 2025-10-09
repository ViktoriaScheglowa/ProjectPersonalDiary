from django import template

register = template.Library()

@register.simple_tag
def my_custom_tag():
    return "Hello from custom tag"

# Или пример фильтра
@register.filter
def my_custom_filter(value):
    return value
