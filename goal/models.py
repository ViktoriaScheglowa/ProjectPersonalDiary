from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Goal(models.Model):
    PRIORITY_CHOICES = [
        ('low', '🟢 Низкий'),
        ('medium', '🟡 Средний'),
        ('high', '🔴 Высокий'),
    ]

    CATEGORY_CHOICES = [
        ('health', '❤️ Здоровье'),
        ('education', '🎓 Обучение'),
        ('career', '💼 Карьера'),
        ('finance', '💰 Финансы'),
        ('relationships', '👥 Отношения'),
        ('hobby', '🎨 Хобби'),
        ('travel', '✈️ Путешествия'),
        ('other', '🔷 Другое'),
    ]

    title = models.CharField(
        max_length=150,
        verbose_name="Заголовок цели"
    )

    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий"
    )
    photo = models.ImageField(
        upload_to="media/photos/",
        blank=True,
        null=True,
        verbose_name="Фото",
        help_text="Загрузите фото своей цели",
    )
    video = models.FileField(
        upload_to="media/videos/",
        blank=True,
        null=True,
        verbose_name="Видео",
        help_text="Загрузите видео своей цели",
    )
    location = models.CharField(
        max_length=30,
        verbose_name="Место",
        blank=True,
        null=True,
        help_text="Укажите место выполнения цели",
    )
    owner = models.ForeignKey(
        User,
        verbose_name="Владелец",
        on_delete=models.CASCADE,
        related_name='goals'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Публичная цель",
        help_text="Отображать цель в публичной ленте",
    )
    notification_task_id = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name="ID задачи уведомления"
    )
    date_deadline = models.DateField(
        default=timezone.now,
        verbose_name="Дата выполнения",
        help_text="Дата, когда необходимо выполнить цель",
    )
    time_deadline = models.TimeField(
        verbose_name="Время выполнения",
        help_text="Время, когда необходимо выполнить цель",
        blank=True,
        null=True,
    )
    action = models.CharField(
        max_length=50,
        verbose_name="Действие",
        help_text="Конкретное действие для достижения цели",
        blank=True,
        null=True,
    )
    is_progress = models.BooleanField(
        verbose_name="Признак достижения",
        blank=True,
        null=True)
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активная цель"
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Приоритет"
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name="Категория"
    )

    public_post = models.ForeignKey(
        'publications.PublicPost',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Публикация в ленте",
        related_name='goals'
    )

    class Meta:
        verbose_name = "Цель"
        verbose_name_plural = "Цели"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['owner', 'is_active']),
            models.Index(fields=['is_public', 'is_active']),
            models.Index(fields=['date_deadline']),
        ]

    def clean(self):
        """Валидация данных"""
        super().clean()

        if self.date_deadline and self.date_deadline < timezone.now().date():
            raise ValidationError({
                'date_deadline': "Дата выполнения не может быть в прошлом"
            })

        # if self.progress < 0 or self.progress > 100:
        #     raise ValidationError({
        #         'progress': "Прогресс должен быть от 0 до 100%"
        #     })

    def save(self, *args, **kwargs):
        """Переопределение save для автоматической публикации"""
        # self.clean()
        #
        # # Автоматически отмечаем как выполненную при 100% прогрессе
        # if self.progress == 100 and not self.is_completed:
        #     self.is_completed = True
        #     logger.info(f"Цель '{self.title}' автоматически отмечена как выполненная")

        # Сохраняем объект
        super().save(*args, **kwargs)

        # Работаем с публикациями после сохранения
        if self.is_public and not self.public_post:
            self.publish_to_feed()
        elif not self.is_public and self.public_post:
            self.remove_from_feed()

    def publish_to_feed(self):
        """Публикация цели в общую ленту"""
        try:
            from publications.models import PublicPost

            # Формируем содержание для публикации
            content = self.get_display_text()

            # Создаем публикацию
            self.public_post = PublicPost.objects.create(
                user=self.owner,
                content=content[:500],  # Ограничение длины
                post_type='goal',
                is_published=True
            )

            # Сохраняем ссылку на публикацию
            self.save()

            # Публикуем в Telegram
            self.publish_to_telegram()

            logger.info(f"Цель '{self.title}' опубликована в ленте")
            return self.public_post

        except Exception as e:
            logger.error(f"Ошибка публикации цели '{self.title}': {e}")
            return None

    def remove_from_feed(self):
        """Удаление цели из публичной ленты"""
        try:
            if self.public_post:
                self.public_post.delete()
                self.public_post = None
                self.save()
                logger.info(f"Цель '{self.title}' удалена из ленты")
        except Exception as e:
            logger.error(f"Ошибка удаления цели из ленты '{self.title}': {e}")

    def publish_to_telegram(self):
        """Публикация цели в Telegram"""
        try:
            from telegram_bot import TelegramService

            telegram_service = TelegramService()
            message = self.get_telegram_message()

            photo_url = None
            if self.photo:
                photo_url = self.get_absolute_photo_url()

            success = telegram_service.send_to_topic('goals', message, self.is_public, photo_url)

            if success and self.public_post:
                # Сохраняем ID сообщения в публикации
                self.public_post.telegram_message_id = success.get('result', {}).get('message_id')
                self.public_post.save()

            return success

        except Exception as e:
            logger.error(f"Ошибка публикации цели в Telegram '{self.title}': {e}")
            return False

    def get_absolute_photo_url(self):
        """Получение абсолютного URL фото"""
        if self.photo:
            from django.conf import settings
            return f"{settings.BASE_URL}{self.photo.url}"
        return None

    def get_telegram_message(self):
        """Форматирование сообщения для Telegram"""
        message = f"🎯 <b>Новая цель!</b>\n\n"
        message += f"👤 <b>Автор:</b> {self.owner.username}\n"
        message += f"🎯 <b>Цель:</b> {self.title}\n"

        if self.description:
            message += f"📝 <b>Описание:</b> {self.description}\n"

        if self.action:
            message += f"🔹 <b>Действие:</b> {self.action}\n"

        if self.location:
            message += f"📍 <b>Место:</b> {self.location}\n"

        if self.date_deadline:
            days_left = self.get_days_left()
            message += f"📅 <b>Срок:</b> {self.date_deadline.strftime('%d.%m.%Y')} "
            if days_left == 0:
                message += "(сегодня!)\n"
            elif days_left == 1:
                message += "(завтра)\n"
            else:
                message += f"(осталось {days_left} дней)\n"

        if self.time_deadline:
            message += f"🕐 <b>Время:</b> {self.time_deadline.strftime('%H:%M')}\n"

        message += f"📊 <b>Прогресс:</b> {self.progress}%\n"

        # Приоритет и категория
        priority_icons = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
        message += f"⚡ <b>Приоритет:</b> {priority_icons.get(self.priority, '⚪')} {self.get_priority_display()}\n"
        message += f"🏷️ <b>Категория:</b> {self.get_category_display()}\n"

        if self.comments:
            message += f"💬 <b>Комментарий:</b> {self.comments}\n"

        status = "✅ Выполнена" if self.is_completed else "🔄 В процессе"
        message += f"📈 <b>Статус:</b> {status}\n"

        return message

    def update_progress(self, new_progress):
        """Обновление прогресса цели"""
        if 0 <= new_progress <= 100:
            self.progress = new_progress
            if new_progress == 100:
                self.is_completed = True
            self.save()
            logger.info(f"Прогресс цели '{self.title}' обновлен до {new_progress}%")
            return True
        return False

    def get_days_left(self):
        """Получить количество дней до дедлайна"""
        if not self.date_deadline:
            return None
        today = timezone.now().date()
        days_left = (self.date_deadline - today).days
        return max(days_left, 0)

    def get_display_text(self):
        """Форматированный текст для отображения"""
        text = f"🎯 {self.title}\n\n"

        if self.description:
            text += f"📝 {self.description}\n\n"

        if self.action:
            text += f"🔹 Действие: {self.action}\n"
        if self.location:
            text += f"📍 Место: {self.location}\n"
        if self.date_deadline:
            days_left = self.get_days_left()
            text += f"📅 Срок: {self.date_deadline.strftime('%d.%m.%Y')} "
            if days_left == 0:
                text += "(сегодня!)\n"
            elif days_left == 1:
                text += "(завтра)\n"
            else:
                text += f"(осталось {days_left} дней)\n"
        if self.time_deadline:
            text += f"🕐 Время: {self.time_deadline.strftime('%H:%M')}\n"

        text += f"📊 Прогресс: {self.progress}%\n"

        # Приоритет и категория
        priority_icons = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
        text += f"⚡ Приоритет: {priority_icons.get(self.priority, '⚪')} {self.get_priority_display()}\n"
        text += f"🏷️ Категория: {self.get_category_display()}\n"

        if self.comments:
            text += f"💬 Комментарий: {self.comments}\n"

        # Статус выполнения
        if self.is_completed:
            text += "✅ Цель достигнута!\n"
        else:
            text += "🔄 В процессе\n"

        status = "🔓 Публичная" if self.is_public else "🔒 Приватная"
        text += f"👁 {status}"

        return text

    def __str__(self):
        return f"{self.title} ({self.owner.username})"

    @property
    def is_overdue(self):
        """Просрочена ли цель"""
        if not self.date_deadline or self.is_completed:
            return False
        return self.date_deadline < timezone.now().date()

    @classmethod
    def get_user_goals(cls, user, include_completed=False):
        """Получить цели пользователя"""
        queryset = cls.objects.filter(owner=user, is_active=True)
        if not include_completed:
            queryset = queryset.filter(is_completed=False)
        return queryset

    @classmethod
    def get_public_goals(cls):
        """Получить публичные цели"""
        return cls.objects.filter(is_public=True, is_active=True)
