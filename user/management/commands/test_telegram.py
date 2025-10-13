from django.core.management.base import BaseCommand
import requests
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_URL
from user.models import User
from habits.tasks import send_test_message


class Command(BaseCommand):
    help = "Тестирование отправки сообщений в Telegram"

    def add_arguments(self, parser):
        parser.add_argument(
            "--chat_id", type=str, help="Конкретный chat_id для тестирования"
        )
        parser.add_argument(
            "--user_id", type=int, help="ID пользователя для тестирования"
        )

    def handle(self, *args, **options):
        chat_id = options.get("chat_id")
        user_id = options.get("user_id")

        if chat_id:
            # Тестируем конкретный chat_id
            self.test_specific_chat_id(chat_id)
        elif user_id:
            # Тестируем конкретного пользователя
            self.test_specific_user(user_id)
        else:
            # Тестируем всех пользователей с chat_id
            self.test_all_users()

    def test_specific_chat_id(self, chat_id):
        """Тестирование конкретного chat_id"""
        self.stdout.write(
            self.style.SUCCESS(f"🧪 Тестирование отправки на chat_id: {chat_id}")
        )

        # Тест через Celery
        result = send_test_message.delay(chat_id, "Тестовое сообщение через Celery")
        self.stdout.write(
            self.style.SUCCESS(f"✅ Задача Celery отправлена: {result.id}")
        )

        # Тест напрямую
        success = self.send_direct_message(chat_id, "Тестовое сообщение напрямую")
        if success:
            self.stdout.write(self.style.SUCCESS("✅ Прямая отправка успешна"))
        else:
            self.stdout.write(self.style.ERROR("❌ Прямая отправка не удалась"))

    def test_specific_user(self, user_id):
        """Тестирование конкретного пользователя"""
        try:
            user = User.objects.get(id=user_id)
            if user.chat_id:
                self.test_specific_chat_id(user.chat_id)
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ У пользователя {user.email} нет chat_id")
                )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ Пользователь с ID {user_id} не найден")
            )

    def test_all_users(self):
        """Тестирование всех пользователей с chat_id"""
        users_with_chat_id = User.objects.exclude(chat_id__isnull=True).exclude(
            chat_id=""
        )

        if users_with_chat_id.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"🧪 Тестирование {users_with_chat_id.count()} пользователей с chat_id..."
                )
            )

            for user in users_with_chat_id:
                self.stdout.write(
                    self.style.WARNING(
                        f"   Тестирование {user.email} (Chat ID: {user.chat_id})"
                    )
                )
                self.test_specific_chat_id(user.chat_id)
        else:
            self.stdout.write(
                self.style.WARNING("ℹ️  Пользователей с chat_id не найдено")
            )

    def send_direct_message(self, chat_id, message):
        """Прямая отправка сообщения в Telegram"""
        try:
            url = f"{TELEGRAM_URL}{TELEGRAM_BOT_TOKEN}/sendMessage"
            params = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
            response = requests.post(url, json=params, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
            return False
