from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Myidea(models.Model):
    CATEGORY_CHOICES = [
        ('business', '💼 Бизнес'),
        ('creative', '🎨 Творчество'),
        ('technology', '💻 Технологии'),
        ('improvement', '🔧 Улучшение'),
        ('personal', '👤 Личное'),
        ('other', '🔷 Другое'),
    ]

    STATUS_CHOICES = [
        ('new', '🆕 Новая'),
        ('in_progress', '🔄 В работе'),
        ('completed', '✅ Реализована'),
        ('postponed', '⏸️ Отложена'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name="Название идеи"
    )
    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий",
        help_text="Дополнительные комментарии к идее"
    )
    pictures = models.ImageField(
        upload_to="idea/photos/",
        blank=True,
        null=True,
        verbose_name="Фото/Схема",
        help_text="Загрузите визуализацию идеи",
    )
    owner = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name='ideas'
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
        verbose_name="Публичная идея",
        help_text="Поделиться идеей с сообществом",
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name="Категория"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус"
    )

    tags = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Теги",
        help_text="Ключевые слова через запятую"
    )

    estimated_effort = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Оценка усилий",
        help_text="Например: 2 недели, 1 месяц и т.д."
    )

    public_post = models.ForeignKey(
        'publications.PublicPost',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Публикация в ленте",
        related_name='ideas'
    )

    class Meta:
        verbose_name = "Идея"
        verbose_name_plural = "Идеи"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['is_public', 'status']),
            models.Index(fields=['category']),
        ]

    def save(self, *args, **kwargs):
        """Переопределение save для автоматической публикации"""
        # Сохраняем объект
        super().save(*args, **kwargs)

        # Работаем с публикациями после сохранения
        if self.is_public and not self.public_post:
            self.publish_to_feed()
        elif not self.is_public and self.public_post:
            self.remove_from_feed()

    def publish_to_feed(self):
        """Публикация идеи в общую ленту"""
        try:
            from publications.models import PublicPost

            # Формируем содержание для публикации
            content = self.get_display_text()

            # Создаем публикацию
            self.public_post = PublicPost.objects.create(
                user=self.owner,
                content=content[:500],
                post_type='idea',
                is_published=True
            )

            # Сохраняем ссылку на публикацию
            self.save()

            # Публикуем в Telegram
            self.publish_to_telegram()

            logger.info(f"Идея '{self.title}' опубликована в ленте")
            return self.public_post

        except Exception as e:
            logger.error(f"Ошибка публикации идеи '{self.title}': {e}")
            return None

    def remove_from_feed(self):
        """Удаление идеи из публичной ленты"""
        try:
            if self.public_post:
                self.public_post.delete()
                self.public_post = None
                self.save()
                logger.info(f"Идея '{self.title}' удалена из ленты")
        except Exception as e:
            logger.error(f"Ошибка удаления идеи из ленты '{self.title}': {e}")

    def publish_to_telegram(self):
        """Публикация идеи в Telegram"""
        try:
            from telegram_bot import TelegramService

            telegram_service = TelegramService()
            message = self.get_telegram_message()

            # photo_url = None
            # if self.pictures:
            #     photo_url = self.get_absolute_photo_url()

            success = telegram_service.send_to_topic('ideas', message, self.is_public)

            if success and self.public_post:
                self.public_post.telegram_message_id = success.get('result', {}).get('message_id')
                self.public_post.save()

            return success

        except Exception as e:
            logger.error(f"Ошибка публикации идеи в Telegram '{self.title}': {e}")
            return False

    def get_absolute_photo_url(self):
        """Получение абсолютного URL фото"""
        if self.pictures:
            from django.conf import settings
            return f"{settings.BASE_URL}{self.pictures.url}"
        return None

    def get_telegram_message(self):
        """Форматирование сообщения для Telegram"""
        message = f"💡 <b>Новая идея!</b>\n\n"
        if self.owner:
            owner_name = self.owner.first_name or self.owner.email.split('@')[0]
            message += f"👤 <b>Автор:</b> {owner_name}\n"
        message += f"💡 <b>Идея:</b> {self.title}\n"

        if self.comments:
            message += f"💬 <b>Комментарий:</b> {self.comments}\n"

        if hasattr(self, 'get_category_display'):
            message += f"🏷️ <b>Категория:</b> {self.get_category_display()}\n"

        if hasattr(self, 'get_status_display'):
            message += f"📊 <b>Статус:</b> {self.get_status_display()}\n"

        if self.tags:
            message += f"🔖 <b>Теги:</b> {self.tags}\n"

        if self.estimated_effort:
            message += f"⏱️ <b>Оценка усилий:</b> {self.estimated_effort}\n"

        message += f"📅 <b>Создана:</b> {self.created_at.strftime('%d.%m.%Y %H:%M')}\n"

        return message

    def get_display_text(self):
        """Форматированный текст для отображения"""
        text = f"💡 {self.title}\n\n"

        if self.comments:
            text += f"💬 Комментарий: {self.comments[:100] + "..."}\n\n"

        text += f"🏷️ Категория: {self.get_category_display()}\n"
        text += f"📊 Статус: {self.get_status_display()}\n"

        if self.tags:
            text += f"🔖 Теги: {self.tags}\n"

        if self.estimated_effort:
            text += f"⏱️ Оценка усилий: {self.estimated_effort}\n"

        text += f"📅 Создана: {self.created_at.strftime('%d.%m.%Y %H:%M')}\n"

        status = "🔓 Публичная" if self.is_public else "🔒 Приватная"
        text += f"👁 {status}"

        return text

    def __str__(self):
        return f"{self.title} ({self.owner.username})"

    @classmethod
    def get_user_ideas(cls, user):
        """Получить идеи пользователя"""
        return cls.objects.filter(owner=user)

    @classmethod
    def get_public_ideas(cls):
        """Получить публичные идеи"""
        return cls.objects.filter(is_public=True)

    def update_status(self, new_status):
        """Обновление статуса идеи"""
        if new_status in dict(self.STATUS_CHOICES):
            self.status = new_status
            self.save()
            logger.info(f"Статус идеи '{self.title}' изменен на {new_status}")
            return True
        return False
