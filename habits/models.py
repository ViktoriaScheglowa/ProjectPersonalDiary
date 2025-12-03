from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from user.models import User


class Habit(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, verbose_name="Автор", null=True, blank=True
    )
    location = models.CharField(
        max_length=30,
        verbose_name="Место",
        help_text="Место, в котором необходимо выполнять привычку",
    )
    photo = models.ImageField(
        upload_to="media/photos/",
        blank=True,
        null=True,
        verbose_name="Фото",
        help_text="Загрузите фото интересного события",
    )
    video = models.FileField(
        upload_to="media/videos/",
        blank=True,
        null=True,
        verbose_name="Видео",
        help_text="Загрузите видео интересного события",
    )
    date_deadline = models.DateField(
        default=timezone.now,
        verbose_name="Дата выполнения привычки",
        help_text="Дата, когда необходимо выполнять привычку",
    )
    time_deadline = models.TimeField(
        verbose_name="Время выполнения привычки",
        help_text="Время, когда необходимо выполнять привычку",
    )
    action = models.CharField(
        max_length=50,
        verbose_name="Действие",
        help_text="Действие, которое представляет собой привычка",
    )
    comments = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    is_enjoyable = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки",
        help_text="Привычка, способ вознаградить себя за выполнение полезной привычки",
        null=True,
        blank=True,
    )
    associated_habit = models.ForeignKey(
        "Habit",
        on_delete=models.CASCADE,
        verbose_name="Связанная привычка",
        help_text="Привычка, которая связана с другой привычкой, важно указывать для полезных привычек, но не для приятных",
        null=True,
        blank=True,
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Периодичность",
        help_text="Периодичность выполнения привычки для напоминания в днях",
    )
    reward = models.CharField(
        max_length=50,
        verbose_name="Вознаграждение",
        help_text="Вознаграждение за выполнение привычки",
        blank=True,
        null=True,
        default=""
    )
    time_to_complete = models.PositiveIntegerField(
        verbose_name="Время на выполнение",
        help_text="Время, которое предположительно нужно потратить на выполнение привычки. Укажите в минутах",
        null=True,
        blank=True,
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Признак публичности",
    )
    telegram_chat_id = models.CharField(
        max_length=20,
        verbose_name="Telegram Chat ID",
        blank=True,
        null=True
    )
    notification_sent = models.BooleanField(
        default=False,
        verbose_name="Уведомление отправлено"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Признак активности"
    )

    public_post = models.ForeignKey(
        'publications.PublicPost',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Публикация в ленте"
    )

    def clean(self):
        """Валидация данных"""
        if self.is_enjoyable and self.reward:
            raise ValidationError("Приятная привычка не может иметь вознаграждение")

        if self.is_enjoyable and self.associated_habit:
            raise ValidationError("Приятная привычка не может иметь связанную привычку")

        if self.associated_habit and self.reward:
            raise ValidationError("Нельзя указывать и связанную привычку, и вознаграждение одновременно")

    def save(self, *args, **kwargs):
            """Переопределение save для автоматической публикации"""
            self.clean()

            # Сначала сохраняем
            super().save(*args, **kwargs)

            # Затем работаем с публикациями
            if self.is_public and not self.public_post:
                self.publish_to_feed()
            elif not self.is_public and self.public_post:
                self.remove_from_feed()

    def publish_to_feed(self):
        """Публикация привычки в общую ленту"""
        try:
            from publications.models import PublicPost

            # Формируем содержание для публикации
            content = f"{self.action}"
            if self.location:
                content += f" в {self.location}"
            if self.time_to_complete:
                content += f" ({self.time_to_complete} мин)"
            if self.comments:
                content += f" - {self.comments}"

            # Создаем публикацию
            self.public_post = PublicPost.objects.create(
                user=self.owner,
                content=content,
                post_type='habit',
                is_published=True
            )

            # Публикуем в Telegram
            self.publish_to_telegram()

            return self.public_post

        except Exception as e:
            print(f"Ошибка публикации привычки: {e}")
            return None

    def remove_from_feed(self):
        """Удаление привычки из публичной ленты"""
        if self.public_post:
            self.public_post.delete()
            self.public_post = None

    def publish_to_telegram(self):
        """Публикация привычки в Telegram"""
        try:
            from telegram_bot import TelegramService

            telegram_service = TelegramService()
            message = self.get_telegram_message()  # Используйте существующий метод

            # Отправляем сообщение
            success = telegram_service.send_to_topic('habits', message, self.is_public)

            if success and self.public_post:
                # Сохраняем ID сообщения в публикации
                self.public_post.telegram_message_id = success.get('result', {}).get('message_id')
                self.public_post.save()

            return success

        except Exception as e:
            print(f"Ошибка публикации в Telegram: {e}")
            return False

    def get_telegram_message(self):
        """Форматирование сообщения для Telegram"""
        message = f"📋 <b>Новая привычка!</b>\n\n"

        if self.owner:
            owner_name = self.owner.first_name or self.owner.email.split('@')[0]
            message += f"👤 <b>Автор:</b> {owner_name}\n"

        message += f"📋 <b>Привычка:</b> {self.action}\n"

        if self.location:
            message += f"📍 <b>Место:</b> {self.location}\n"

        if self.time_deadline:
            message += f"🕐 <b>Время:</b> {self.time_deadline.strftime('%H:%M')}\n"

        message += f"📅 <b>Периодичность:</b> каждые {self.periodicity} дней\n"

        if self.time_to_complete:
            message += f"⏱ <b>Время на выполнение:</b> {self.time_to_complete} мин\n"

        if self.comments:
            message += f"📝 <b>Комментарий:</b> {self.comments}\n"

        return message

    def get_display_text(self):
        """Форматированный текст для отображения"""
        text = f"🔹 {self.action}\n"
        if self.location:
            text += f"📍 Место: {self.location}\n"
        if self.time_deadline:
            text += f"🕐 Время: {self.time_deadline.strftime('%H:%M')}\n"
        if self.periodicity > 1:
            text += f"📅 Периодичность: каждые {self.periodicity} дней\n"
        else:
            text += f"📅 Периодичность: ежедневно\n"
        if self.time_to_complete:
            text += f"⏱ Время на выполнение: {self.time_to_complete} мин\n"
        if self.reward:
            text += f"🎁 Вознаграждение: {self.reward}\n"
        if self.comments:
            text += f"📝 Комментарий: {self.comments}\n"

        status = "🔓 Публичная" if self.is_public else "🔒 Приватная"
        text += f"👁 {status}"

        return text

    def __str__(self):
        return f"{self.action} в {self.time_deadline} ({self.location})"

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ['id']
