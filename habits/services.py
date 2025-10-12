import datetime
import json

import requests
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from config.settings import TELEGRAM_URL, TELEGRAM_BOT_TOKEN


def send_telegram_message(message, chat_id):
    """Отправка сообщения в Telegram"""
    try:
        url = f"{TELEGRAM_URL}{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=params, timeout=10)
        response.raise_for_status()
        print(f"✅ Сообщение отправлено в Telegram для chat_id: {chat_id}")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP ошибка отправки Telegram сообщения: {e}")
        print(f"   Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Ошибка отправки Telegram сообщения: {e}")
        return False


def set_schedule_for_habit(habit):
    """Создание периодической задачи для привычки"""
    try:
        # Удаляем старую задачу, если существует
        old_task_name = f"Habit Reminder {habit.id}"
        PeriodicTask.objects.filter(name=old_task_name).delete()

        # Создаем интервал на основе периодичности привычки
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=habit.periodicity,
            period=IntervalSchedule.DAYS,
        )

        # Создаем периодическую задачу
        PeriodicTask.objects.create(
            interval=schedule,
            name=old_task_name,
            task="habits.tasks.send_reminder_with_bot",
            args=json.dumps([]),
            kwargs=json.dumps({}),
            start_time=datetime.datetime.now() + datetime.timedelta(minutes=1),
            expires=datetime.datetime.now() + datetime.timedelta(days=365),
            enabled=True,
        )
        print(f"✅ Периодическая задача создана для привычки {habit.id}")
        return True
    except Exception as e:
        print(f"❌ Ошибка создания периодической задачи: {e}")
        return False


def send_immediate_reminder(habit):
    """Немедленная отправка напоминания о привычке"""
    if habit.owner and habit.owner.chat_id:
        message = (
            f"🔔 Срочное напоминание о привычке!\n"
            f"📝 Действие: {habit.action}\n"
            f"🕐 Время: {habit.time_deadline}\n"
            f"📍 Место: {habit.location}\n"
            f"📅 Дата: {habit.date_deadline}"
        )
        return send_telegram_message(message, habit.owner.chat_id)
    return False