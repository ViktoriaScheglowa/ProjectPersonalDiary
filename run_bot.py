import os
import sys
import django

# Добавляем текущую директорию в Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Теперь импортируем бота
try:
    from telegram_bot import TelegramBot

    print("🤖 Starting Telegram bot...")

    bot = TelegramBot()
    bot.run()

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("📁 Проверьте что файл telegram_bot.py находится в корне проекта")
    print("📁 И что в нем есть класс TelegramBot")
except Exception as e:
    print(f"❌ Ошибка запуска бота: {e}")
    import traceback

    traceback.print_exc()
