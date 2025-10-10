from django.db import models
from django.utils import timezone

from user.models import User


class Goal(models.Model):
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
        help_text="Загрузите фото своей цели")
    video = models.FileField(
        upload_to='media/videos',
        blank=True,
        null=True,
        verbose_name="Видео",
        help_text="Загрузите видео своей цели")
    location = models.CharField(
        max_length=30,
        verbose_name="Место",
        blank=True,
        null=True,
        help_text="Укажите место своей цели")
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
                                    help_text="Интересные цели можно публиковать в общий доступ")
    notification_task_id = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="id задачи уведомления")
    date_deadline = models.DateField(
        default=timezone.now,
        verbose_name="Дата выполнения цели",
        help_text="Дата, когда необходимо выполнять цель",)
    time_deadline = models.TimeField(
        verbose_name="Время выполнения цели",
        help_text="Время, когда необходимо выполнять цель",
        blank=True,
        null=True,
    )
    action = models.CharField(
        max_length=50,
        verbose_name="Действие",
        help_text="Действие, которое представляет собой цель",
        blank=True,
        null=True,
    )
    is_progress = models.BooleanField(
        verbose_name="Признак достижения",
        help_text="Достижение цели",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(verbose_name="Признак активности", default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Цели пользователя {self.owner} от {self.created_at.strftime('%Y-%m-%d %H:%M')}"
