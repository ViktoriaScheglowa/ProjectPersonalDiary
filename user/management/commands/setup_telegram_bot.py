from django.core.management.base import BaseCommand
import requests
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_URL


class Command(BaseCommand):
    help = 'Настройка Telegram бота'

    def handle(self, *args, **options):
        # Проверка токена бота
        url = f"{TELEGRAM_URL}{TELEGRAM_BOT_TOKEN}/getMe"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Бот успешно подключен!\n"
                        f"🤖 Имя бота: {bot_info['result']['first_name']}\n"
                        f"🔗 Username: @{bot_info['result']['username']}"
                    )
                )

                # Получение последних обновлений для получения chat_id
                updates_url = f"{TELEGRAM_URL}{TELEGRAM_BOT_TOKEN}/getUpdates"
                updates_response = requests.get(updates_url, timeout=10)

                if updates_response.status_code == 200:
                    updates = updates_response.json()
                    if updates['result']:
                        self.stdout.write(
                            self.style.SUCCESS(
                                "📨 Найдены сообщения от пользователей:"
                            )
                        )
                        for update in updates['result']:
                            if 'message' in update:
                                chat_id = update['message']['chat']['id']
                                username = update['message']['chat'].get('username', 'Не указан')
                                first_name = update['message']['chat'].get('first_name', 'Не указан')
                                self.stdout.write(
                                    f"   👤 {first_name} (@{username}) - Chat ID: {chat_id}"
                                )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                "ℹ️  Сообщений от пользователей пока нет. "
                                "Напишите боту в Telegram, чтобы получить ваш Chat ID."
                            )
                        )

            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Ошибка подключения к боту: {response.json()}"
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Ошибка: {e}")
            )
