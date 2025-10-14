from django import template
from django.template.defaultfilters import filesizeformat

register = template.Library()


@register.simple_tag
def my_custom_tag():
    return "Hello from custom tag"


@register.filter
def my_custom_filter(value):
    return value


@register.filter
def media_filter(path):
    """
    Фильтр для отображения медиа-файлов
    Если путь пустой, возвращает пустую строку
    """
    if path:
        return f"/media/{path}"
    return ""


@register.filter
def file_type(value):
    """Определяет тип файла по расширению"""
    if hasattr(value, "name"):
        filename = value.name.lower()
        if filename.endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp")):
            return "image"
        elif filename.endswith((".mp4", ".avi", ".mov", ".wmv")):
            return "video"
        elif filename.endswith((".pdf", ".doc", ".docx")):
            return "document"
    return "unknown"


@register.filter
def file_size(value):
    """Возвращает размер файла в читаемом формате"""
    if hasattr(value, "size"):
        return filesizeformat(value.size)
    return ""
