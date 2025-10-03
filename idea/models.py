from django.db import models
from django.conf import settings


class Myidea(models.Model):
    title = models.CharField(
        max_length=150,
        verbose_name='Заголовок')
    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name='Коментарий')
    pictures = models.ImageField(
        upload_to='media/photos',
        blank=True,
        null=True,
        verbose_name='Фото',
        help_text="Загрузите картинки своих мыслей")
    owner = models.ForeignKey("user.User",
                              verbose_name='Владелец',
                              help_text='Укажите владельца',
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True,
                                     verbose_name='Дата обновления мыслей')
    is_public = models.BooleanField(default=False,
                                    verbose_name="Признак публичности",
                                    help_text="Интересные мысли можно публиковать в общий доступ")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Мысли пользователя {self.user.username} от {self.created_at.strftime('%Y-%m-%d %H:%M')}"

