from django import template

register = template.Library()


@register.simple_tag
def get_user_avatar(user):
    """Возвращает аватар пользователя"""
    if hasattr(user, "avatar") and user.avatar:
        return user.avatar.url
    elif (
        hasattr(user, "profile")
        and hasattr(user.profile, "avatar")
        and user.profile.avatar
    ):
        return user.profile.avatar.url
    return None
