from django import template

register = template.Library()


@register.simple_tag
def my_custom_tag():
    return "Hello from custom tag"


@register.filter
def my_custom_filter(value):
    return value


@register.simple_tag
def current_time(format_string):
    from django.utils import timezone

    return timezone.now().strftime(format_string)


@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})


@register.filter
def media_filter(path):
    """
    Фильтр для отображения медиа-файлов
    """
    if path:
        return f"/media/{path}"
    return ""
