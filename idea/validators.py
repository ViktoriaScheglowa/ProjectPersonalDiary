from datetime import date

from packaging.utils import _
from rest_framework.exceptions import ValidationError


class OffensiveWordValidator:
    """
    Валидатор, проверяющий наличие запрещенных слов.
    """

    def __init__(self, forbidden_words=None, comments=None):
        self.forbidden_words = forbidden_words if forbidden_words is not None else ['плохо', 'ужасно']
        self.comments = comments or _("Коментарий содержит запрещенное слово: '%(word)s'.")

    def __call__(self, value):
        value_lower = value.lower()
        for word in self.forbidden_words:
            if word in value_lower:
                raise ValidationError(
                    self.comments,
                    params={'word': word},
                    code='offensive_content'
                )

    def __eq__(self, other):
        return (
                isinstance(other, self.__class__) and
                self.forbidden_words == other.forbidden_words and
                self.comments == other.comments
        )


# Валидатор для условной длины (если значение есть)
class ConditionalLengthValidator:
    """
    Валидатор, который срабатывает, только если значение не является пустой строкой или None.
    """

    def __init__(self, min_length=20, comments=None):
        self.min_length = min_length
        self.comments = comments or _(
            'Если вы оставили комментарий, он должен быть подробнее (минимум %(min_length)d символов).')

    def __call__(self, value):
        # Проверяем, что значение существует (для строк: не None и не пустая строка)
        if value:
            if len(value) < self.min_length:
                raise ValidationError(
                    self.comments,
                    params={'min_length': self.min_length},
                    code='comment_too_short_if_provided'
                )

    def __eq__(self, other):
        return (
                isinstance(other, self.__class__) and
                self.min_length == other.min_length and
                self.comments == other.comments
        )
