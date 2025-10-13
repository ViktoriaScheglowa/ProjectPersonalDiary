from celery import shared_task
from django.utils import timezone
from datetime import datetime
import requests
from django.conf import settings
from .models import Habit


def send_telegram_message(message, chat_id):
    """Функция отправки сообщения в Telegram"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    if isinstance(chat_id, str) and chat_id.isdigit():
        chat_id = int(chat_id)

    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ Уведомление отправлено для chat_id {chat_id}")
            return True
        else:
            print(f"❌ Ошибка отправки: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False


@shared_task
def send_reminder_with_bot():
    """Отправка напоминания о привычке с помощью телеграм-бота."""
    try:
        today = timezone.now().date()
        current_time = timezone.now().time()

        habits = Habit.objects.filter(
            date_deadline=today,
            time_deadline__hour=current_time.hour,
            time_deadline__minute=current_time.minute,
            is_active=True,
        ).select_related("owner")

        sent_count = 0
        error_count = 0

        print(f"🔍 Проверка привычек в {current_time.strftime('%H:%M')}")

        for habit in habits:
            chat_id = getattr(habit, "telegram_chat_id", None)
            if not chat_id and habit.owner and hasattr(habit.owner, "profile"):
                chat_id = getattr(habit.owner.profile, "telegram_chat_id", None)

            if chat_id:
                message = (
                    f"🔔 <b>Время выполнить привычку!</b>\n\n"
                    f"📝 Действие: {habit.action}\n"
                    f"🕐 Время: {habit.time_deadline.strftime('%H:%M')}\n"
                    f"📍 Место: {habit.location}\n"
                    f"📅 Дата: {habit.date_deadline.strftime('%d.%m.%Y')}\n\n"
                    f"💪 Не пропустите!"
                )

                success = send_telegram_message(message, chat_id)
                if success:
                    sent_count += 1
                    print(f"✅ Напоминание отправлено для привычки: {habit.action}")
                else:
                    error_count += 1
                    print(f"❌ Ошибка отправки для привычки: {habit.action}")
            else:
                print(f"⚠️ Нет chat_id для привычки: {habit.action}")

        print(f"📊 Итог: отправлено {sent_count}, ошибок {error_count}")
        return f"Отправлено: {sent_count}, Ошибок: {error_count}"

    except Exception as e:
        print(f"❌ Ошибка в задаче send_reminder_with_bot: {e}")
        return f"Ошибка: {e}"


@shared_task
def send_test_message(chat_id, message="Тестовое сообщение от Celery"):
    """Тестовая задача для отправки сообщения"""
    try:
        success = send_telegram_message(message, chat_id)
        if success:
            print(f"✅ Тестовое сообщение отправлено на chat_id: {chat_id}")
            return True
        else:
            print(f"❌ Ошибка отправки тестового сообщения на chat_id: {chat_id}")
            return False
    except Exception as e:
        print(f"❌ Ошибка в тестовой задаче: {e}")
        return False


@shared_task
def check_habits_for_notification():
    """Проверка привычек для отправки уведомлений (альтернативная версия)"""
    send_reminder_with_bot.delay()


@shared_task
def reset_notification_status():
    """Сброс статуса уведомлений для новых дней"""
    today = timezone.now().date()
    updated = Habit.objects.filter(date_deadline__lt=today).update(
        notification_sent=False
    )

    print(f"🔄 Сброшено статусов уведомлений: {updated}")


@shared_task
def test_celery_worker():
    """Тестовая задача для проверки работы Celery"""
    print("✅ Celery worker работает корректно!")
    return "Celery is working!"
