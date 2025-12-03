from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Moment(models.Model):
    MOOD_CHOICES = [
        ('happy', '😊 Счастливый'),
        ('excited', '🎉 Восторг'),
        ('peaceful', '😌 Спокойный'),
        ('inspired', '💡 Вдохновение'),
        ('proud', '🏆 Гордость'),
        ('grateful', '🙏 Благодарность'),
        ('funny', '😄 Смешной'),
        ('other', '🔷 Другой'),
    ]

    CATEGORY_CHOICES = [
        ('nature', '🌳 Природа'),
        ('travel', '✈️ Путешествия'),
        ('family', '👨‍👩‍👧‍👦 Семья'),
        ('friends', '👫 Друзья'),
        ('achievement', '🏅 Достижение'),
        ('celebration', '🎊 Праздник'),
        ('daily', '📅 Повседневность'),
        ('creative', '🎨 Творчество'),
        ('other', '🔷 Другое'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name="Название момента"
    )
    comments = models.TextField(
        verbose_name="Описание момента",
        help_text="Опишите что это за момент и почему он важен"
    )
    photo = models.ImageField(
        upload_to="media/photos/",
        blank=True,
        null=True,
        verbose_name="Фото",
        help_text="Загрузите фото момента",
    )
    video = models.FileField(
        upload_to="media/videos/",
        blank=True,
        null=True,
        verbose_name="Видео",
        help_text="Загрузите видео момента",
    )
    location = models.CharField(
        max_length=100,
        verbose_name="Место",
        blank=True,
        null=True,
        help_text="Где произошел этот момент",
    )
    owner = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='moments'
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
        verbose_name="Публичный момент",
        help_text="Поделиться моментом с сообществом",
    )
    mood = models.CharField(
        max_length=20,
        choices=MOOD_CHOICES,
        default='happy',
        verbose_name="Настроение"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name="Категория"
    )
    event_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата события",
        help_text="Когда произошел этот момент"
    )
    tags = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Теги",
        help_text="Ключевые слова через запятую"
    )

    public_post = models.ForeignKey(
        'publications.PublicPost',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Публикация в ленте",
        related_name='moments'
    )

    class Meta:
        verbose_name = "Момент"
        verbose_name_plural = "Моменты"
        ordering = ["-event_date"]
        indexes = [
            models.Index(fields=['owner', 'event_date']),
            models.Index(fields=['is_public', 'event_date']),
            models.Index(fields=['category', 'mood']),
        ]

    def clean(self):
        """Валидация данных"""
        super().clean()

        if self.event_date and self.event_date > timezone.now():
            raise ValidationError({
                'event_date': "Дата события не может быть в будущем"
            })

    def save(self, *args, **kwargs):
        """Переопределение save для автоматической публикации"""
        self.clean()

        # Сохраняем объект
        super().save(*args, **kwargs)

        # Работаем с публикациями после сохранения
        if self.is_public and not self.public_post:
            self.publish_to_feed()
        elif not self.is_public and self.public_post:
            self.remove_from_feed()

    def publish_to_feed(self):
        """Публикация момента в общую ленту"""
        try:
            from publications.models import PublicPost

            # Формируем содержание для публикации
            content = self.get_display_text()

            # Создаем публикацию
            self.public_post = PublicPost.objects.create(
                user=self.owner,
                content=content[:500],
                post_type='moment',
                is_published=True
            )

            # Сохраняем ссылку на публикацию
            self.save()

            # Публикуем в Telegram
            self.publish_to_telegram()

            logger.info(f"Момент '{self.title}' опубликован в ленте")
            return self.public_post

        except Exception as e:
            logger.error(f"Ошибка публикации момента '{self.title}': {e}")
            return None

    def remove_from_feed(self):
        """Удаление момента из публичной ленты"""
        try:
            if self.public_post:
                self.public_post.delete()
                self.public_post = None
                self.save()
                logger.info(f"Момент '{self.title}' удален из ленты")
        except Exception as e:
            logger.error(f"Ошибка удаления момента из ленты '{self.title}': {e}")

    def publish_to_telegram(self):
        """Публикация момента в Telegram"""
        try:
            from telegram_bot import TelegramService

            telegram_service = TelegramService()
            message = self.get_telegram_message()

            success = telegram_service.send_to_topic('moments', message, self.is_public)

            if success and self.public_post:
                self.public_post.telegram_message_id = success.get('result', {}).get('message_id')
                self.public_post.save()

            return success

        except Exception as e:
            logger.error(f"Ошибка публикации момента в Telegram '{self.title}': {e}")
            return False

    def get_absolute_photo_url(self):
        """Получение абсолютного URL фото"""
        if self.photo:
            from django.conf import settings
            return f"{settings.BASE_URL}{self.photo.url}"
        return None

    def get_telegram_message(self):
        """Форматирование сообщения для Telegram"""
        message = f"📸 <b>Новый момент!</b>\n\n"
        message += f"👤 <b>Автор:</b> {self.owner.username}\n"
        message += f"📸 <b>Момент:</b> {self.title}\n"
        message += f"📝 <b>Описание:</b> {self.comments}\n"

        if self.location:
            message += f"📍 <b>Место:</b> {self.location}\n"

        message += f"😊 <b>Настроение:</b> {self.get_mood_display()}\n"
        message += f"🏷️ <b>Категория:</b> {self.get_category_display()}\n"

        message += f"📅 <b>Дата события:</b> {self.event_date.strftime('%d.%m.%Y %H:%M')}\n"

        if self.tags:
            message += f"🔖 <b>Теги:</b> {self.tags}\n"

        return message

    def get_display_text(self):
        """Форматированный текст для отображения"""
        text = f"📸 {self.title}\n\n"
        text += f"📝 {self.comments}\n\n"

        if self.location:
            text += f"📍 Место: {self.location}\n"

        text += f"😊 Настроение: {self.get_mood_display()}\n"
        text += f"🏷️ Категория: {self.get_category_display()}\n"

        text += f"📅 Дата события: {self.event_date.strftime('%d.%m.%Y %H:%M')}\n"

        if self.tags:
            text += f"🔖 Теги: {self.tags}\n"

        status = "🔓 Публичный" if self.is_public else "🔒 Приватный"
        text += f"👁 {status}"

        return text

    def __str__(self):
        return f"{self.title} ({self.owner.username})"

    @property
    def time_ago(self):
        """Время с момента события"""
        now = timezone.now()
        diff = now - self.event_date

        if diff.days > 365:
            years = diff.days // 365
            return f"{years} год назад" if years == 1 else f"{years} лет назад"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} месяц назад" if months == 1 else f"{months} месяцев назад"
        elif diff.days > 0:
            return f"{diff.days} дней назад"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} часов назад"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} минут назад"
        else:
            return "только что"

    @classmethod
    def get_user_moments(cls, user):
        """Получить моменты пользователя"""
        return cls.objects.filter(owner=user)

    @classmethod
    def get_public_moments(cls):
        """Получить публичные моменты"""
        return cls.objects.filter(is_public=True)

    @classmethod
    def get_recent_moments(cls, days=7):
        """Получить недавние моменты"""
        from datetime import timedelta
        start_date = timezone.now() - timedelta(days=days)
        return cls.objects.filter(event_date__gte=start_date)
