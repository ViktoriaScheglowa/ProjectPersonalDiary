from django import template
register = template.Library()


@register.filter()
def media_filter(path):
    if path:
        return f"/media/{path}"
    return "#"


@register.simple_tag
def current_time(format_string):
    from django.utils import timezone
    return timezone.now().strftime(format_string)


@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})
