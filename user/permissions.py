from rest_framework import permissions


class IsModer(permissions.BasePermission):
    """Проверяет, является ли пользователь модератором"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="manager").exists()
