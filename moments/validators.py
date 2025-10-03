from datetime import date, datetime

from django.utils import timezone
from rest_framework import serializers


class ValidateCreate:
    def __init__(self, created_at='created_at'):
        self.created_at = created_at

    def __call__(self, attrs):
        value = attrs.get(self.created_at)
        if value is None:
            return  # или: raise serializers.ValidationError({self.created_at: "Обязательное поле."})

        # если приходит datetime, привести к дате с учётом таймзоны
        if isinstance(value, datetime):
            value = timezone.localtime(value).date()

        if value < timezone.localdate():
            raise serializers.ValidationError({
                self.created_at: "Дата создания не может быть раньше сегодняшнего дня."
            })