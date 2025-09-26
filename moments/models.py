from django.db import models
from django.db import models
from django.conf import settings


class Moment(models.Model):
    title = models.CharField(
        max_length=150,
        verbose_name='Заголовок')
    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name='Коментарий')
    photo = models.ImageField(
        upload_to='media/photos',
        blank=True,
        null=True,
        verbose_name='Фото',
        help_text="Загрузите фото интересного события")
    video = models.FileField(
        upload_to='media/videos',
        blank=True,
        null=True,
        verbose_name="Видео",
        help_text="Загрузите видео интересного события")
    location = models.CharField(
        max_length=30,
        verbose_name="Место",
        help_text="Укажите место, в котором происходили интересные события")
    owner = models.ForeignKey("user.User",
                              verbose_name='Владелец',
                              help_text='Укажите владельца',
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True,
                                     verbose_name='Дата обновления момента')
    is_public = models.BooleanField(default=False,
                                    verbose_name="Признак публичности",
                                    help_text="Интересные моменты можно публиковать в общий доступ")
    notification_task_id = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="id задачи уведомления")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Момент пользователя {self.user.username} от {self.created_at.strftime('%Y-%m-%d %H:%M')}"
