import os
import django
import asyncio

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from telegram_bot import TelegramBot

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()