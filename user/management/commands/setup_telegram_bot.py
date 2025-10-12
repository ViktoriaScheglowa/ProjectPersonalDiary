from django.core.management.base import BaseCommand
import requests
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_URL
from user.models import User


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

                # Отправка тестового сообщения пользователям с chat_id
                self.send_test_messages()

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

    def send_test_messages(self):
        """Отправка тестовых сообщений пользователям с chat_id"""
        users_with_chat_id = User.objects.exclude(chat_id__isnull=True).exclude(chat_id='')

        if users_with_chat_id.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n📤 Найдено {users_with_chat_id.count()} пользователей с chat_id. Отправка тестовых сообщений..."
                )
            )

            for user in users_with_chat_id:
                success = self.send_telegram_message(
                    user.chat_id,
                    "✅ Тестовое сообщение от вашего бота!\n"
                    "Это подтверждает, что уведомления работают корректно."
                )
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"   ✅ Сообщение отправлено пользователю {user.email} (Chat ID: {user.chat_id})"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"   ❌ Ошибка отправки пользователю {user.email} (Chat ID: {user.chat_id})"
                        )
                    )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "\nℹ️  Пользователей с chat_id не найдено. "
                    "Добавьте chat_id пользователям в админке."
                )
            )

    def send_telegram_message(self, chat_id, message):
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