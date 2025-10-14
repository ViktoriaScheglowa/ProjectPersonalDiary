from datetime import date

from rest_framework.exceptions import ValidationError


class CheckGoalValidator:
    """
    Исключение, неактивная цель не может быть публичной.
    """

    def __init__(self, is_active, is_public):
        self.is_active = is_active
        self.is_public = is_public

    def __call__(self, attrs):
        is_active = attrs.get(self.is_active)
        is_public = attrs.get(self.is_public)

        if is_public and not is_active:
            raise ValidationError("Неактивная цель не может быть публичной.")
        # return True


class DateDeadlineGoalValidator:
    """Проверка даты на актуальность."""

    def __init__(self, date_deadline):
        self.date_deadline = date_deadline

    def __call__(self, attrs):
        date_deadline = attrs.get(self.date_deadline)

        today = date.today()

        if date_deadline and date_deadline < today:
            raise ValidationError("Цель не может быть достигнута задним числом.")

        # return True
