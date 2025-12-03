# publications/models.py
from django.db import models
from user.models import User


class PublicPost(models.Model):
    POST_TYPES = [
        ('habit', 'Привычка'),
        ('goal', 'Цель'),
        ('idea', 'Идея'),
        ('moment', 'Момент')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='public_posts')
    content = models.TextField(verbose_name='Содержание')
    post_type = models.CharField(max_length=20, choices=POST_TYPES, verbose_name='Тип записи')
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано')
    telegram_message_id = models.IntegerField(null=True, blank=True, verbose_name='ID сообщения в Telegram')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Публичная запись'
        verbose_name_plural = 'Публичные записи'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_post_type_display()} ({self.created_at})"
