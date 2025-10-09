from datetime import timezone

from celery import shared_task


from goal.models import Goal
from goal.services import send_telegram_message


@shared_task
def send_reminder_with_bot(goal_id, messagge):
    """Отправка напоминания о достидении цели с помощью телеграм-бота."""
    today = timezone.now().today()
    goal = Goal.objects.filter(id=goal_id, time_deadline=today)

    if goal.owner.chat_id:
        send_telegram_message(
            "Напоминание: Сегодня нужно {self.action} в {self.time_deadline}.",
            goal.owner.chat_id,
        )
