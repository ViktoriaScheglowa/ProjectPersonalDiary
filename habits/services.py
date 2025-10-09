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
        return True
    except Exception as e:
        print(f"Ошибка отправки Telegram сообщения: {e}")
        return False


def set_schedule_every_day(habit_id, periodicity):
    """Создание периодической задачи для привычки"""
    try:
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=periodicity,
            period=IntervalSchedule.DAYS,
        )

        PeriodicTask.objects.create(
            interval=schedule,
            name=f"Habit Reminder {habit_id}",
            task="habits.tasks.send_reminder_with_bot",
            args=json.dumps([habit_id]),
            kwargs=json.dumps({}),
            expires=datetime.datetime.utcnow() + datetime.timedelta(days=365),
        )
        return True
    except Exception as e:
        print(f"Ошибка создания периодической задачи: {e}")
        return False