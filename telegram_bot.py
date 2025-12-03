import requests
import logging
from django.conf import settings
from asgiref.sync import sync_to_async
from django.utils import timezone
from datetime import time

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.group_id = settings.MAIN_GROUP_ID
        self.public_threads = getattr(settings, 'TELEGRAM_PUBLIC_THREADS', {})
        self.private_threads = getattr(settings, 'TELEGRAM_PRIVATE_THREADS', {})

    def send_message(self, chat_id, text, message_thread_id=None):
        """Отправка сообщения в Telegram"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text
        }

        if message_thread_id:
            payload['message_thread_id'] = message_thread_id

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None

    def send_to_topic(self, content_type, message, is_public=True):
        """Отправка в соответствующую тему"""
        if is_public:
            thread_id = self.public_threads.get(content_type)
        else:
            thread_id = self.private_threads.get(content_type)

        if not thread_id:
            logger.error(f"No thread configured for {content_type}")
            return None

        return self.send_message(self.group_id, message, thread_id)


class TelegramBot:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("register", self.register))
        self.application.add_handler(CommandHandler("habits", self.show_habits))
        self.application.add_handler(CommandHandler("goals", self.show_goals))
        self.application.add_handler(CommandHandler("ideas", self.show_ideas))
        self.application.add_handler(CommandHandler("moments", self.show_moments))
        self.application.add_handler(CommandHandler("public_feed", self.public_feed))
        self.application.add_handler(CommandHandler("channels", self.channels_info))
        self.application.add_handler(CommandHandler("help", self.help_command))

        # Команды создания
        self.application.add_handler(CommandHandler("create_habit", self.create_habit))
        self.application.add_handler(CommandHandler("create_goal", self.create_goal))
        self.application.add_handler(CommandHandler("create_idea", self.create_idea))
        self.application.add_handler(CommandHandler("create_moment", self.create_moment))

        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def get_django_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение пользователя Django по Telegram ID"""
        try:
            from user.models import User

            telegram_user = update.effective_user
            telegram_user_id = str(telegram_user.id)

            @sync_to_async
            def get_or_create_user():
                try:
                    # 1. Пробуем найти по chat_id
                    user = User.objects.get(chat_id=telegram_user_id)
                    logger.info(f"User found by chat_id: {telegram_user_id}")
                    return user
                except User.DoesNotExist:
                    logger.info(f"Creating new user for chat_id: {telegram_user_id}")

                    # 2. Создаем нового пользователя
                    email = f"telegram_{telegram_user_id}@example.com"

                    # Проверяем, не существует ли уже пользователь с таким email
                    if User.objects.filter(email=email).exists():
                        import time
                        email = f"telegram_{telegram_user_id}_{int(time.time())}@example.com"

                    # Создаем пользователя БЕЗ использования create_user
                    # Используем напрямую модель User
                    user = User(
                        email=email,
                        chat_id=telegram_user_id,
                        is_active=True
                    )

                    # Устанавливаем пароль
                    user.set_password('telegram_default_password')

                    # Добавляем имя, если есть в Telegram
                    if telegram_user.first_name:
                        user.first_name = telegram_user.first_name

                    if telegram_user.last_name:
                        user.last_name = telegram_user.last_name

                    # Сохраняем
                    user.save()
                    logger.info(f"New user created: {user.email} with chat_id: {telegram_user_id}")
                    return user
                except Exception as e:
                    logger.error(f"Error in get_or_create_user: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    return None

            user = await get_or_create_user()
            return user

        except Exception as e:
            logger.error(f"Error getting django user: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None


    # ===== МЕТОДЫ СОЗДАНИЯ ЗАПИСЕЙ =====

    async def create_habit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание привычки - УПРОЩЕННАЯ ВЕРСИЯ"""
        try:
            user = await self.get_django_user(update, context)
            if not user:
                await update.message.reply_text("❌ Пользователь не найден. Используйте /start для регистрации")
                return

            if not context.args:
                await update.message.reply_text(
                    "📝 Введите действие для привычки после команды:\n"
                    "Пример: /create_habit медитировать 10 минут"
                )
                return

            action = " ".join(context.args)

            @sync_to_async
            def create_habit_instance(user, action):
                from habits.models import Habit
                from datetime import time

                # Создаем привычку только с обязательными полями
                return Habit.objects.create(
                    owner=user,
                    action=action,
                    location="Дом",
                    time_deadline=time(20, 0),  # 20:00 по умолчанию
                    periodicity=1,
                    is_public=False,
                    is_active=True,
                    date_deadline=timezone.now().date()  # Добавляем обязательное поле
                )

            habit = await create_habit_instance(user, action)
            await update.message.reply_text(f"✅ Привычка создана: {habit.action}")

        except Exception as e:
            logger.error(f"Habit creation error: {e}")
            await update.message.reply_text("❌ Ошибка при создании привычки")

            # Публикация в Telegram
            telegram_service = TelegramService()
            author_name = user.first_name or user.email.split('@')[0]
            message = f"📋 Новая привычка!\n\nДействие: {habit.action}\nАвтор: {author_name}"
            telegram_service.send_to_topic('habits', message, True)

            await update.message.reply_text(f"✅ Привычка создана: {habit.action}")

        except Exception as e:
            logger.error(f"Habit creation error: {e}")
            await update.message.reply_text("❌ Ошибка при создании привычки")

    async def create_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание цели - УПРОЩЕННАЯ ВЕРСИЯ"""
        try:
            user = await self.get_django_user(update, context)
            if not user:
                await update.message.reply_text("❌ Пользователь не найден. Используйте /start для регистрации")
                return

            if not context.args:
                await update.message.reply_text(
                    "🎯 Введите название цели после команды:\n"
                    "Пример: /create_goal Выучить Python"
                )
                return

            title = " ".join(context.args)

            @sync_to_async
            def create_goal_instance(user, title):
                from goal.models import Goal
                from datetime import date

                # Получаем дату на 30 дней вперед как date (не datetime)
                deadline_date = date.today() + timezone.timedelta(days=30)

                try:
                    # Создаем цель без вызова save() (чтобы избежать валидации)
                    goal = Goal(
                        owner=user,
                        title=title,
                        is_public=False,
                        is_active=True,
                        date_deadline=deadline_date
                    )

                    # Сохраняем без вызова полного save()
                    goal.save(force_insert=True, validate=False)
                    return goal
                except Exception as e:
                    # Если не работает, пробуем альтернативный способ
                    logger.error(f"Error creating goal: {e}")
                    goal = Goal.objects.create(
                        owner=user,
                        title=title,
                        is_public=True,
                        is_active=True
                    )
                    return goal

            goal = await create_goal_instance(user, title)

            # Публикация в Telegram
            telegram_service = TelegramService()
            author_name = user.first_name or user.email.split('@')[0]
            message = f"🎯 Новая цель!\n\nЦель: {goal.title}\nАвтор: {author_name}"
            telegram_service.send_to_topic('goals', message, True)

            await update.message.reply_text(f"✅ Цель создана: {goal.title}")

        except Exception as e:
            logger.error(f"Goal creation error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await update.message.reply_text("❌ Ошибка при создании цели")

    async def create_idea(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание идеи - УПРОЩЕННАЯ ВЕРСИЯ"""
        try:
            user = await self.get_django_user(update, context)
            if not user:
                await update.message.reply_text("❌ Пользователь не найден. Используйте /start для регистрации")
                return

            if not context.args:
                await update.message.reply_text(
                    "💡 Введите название идеи после команды:\n"
                    "Пример: /create_idea Новое мобильное приложение"
                )
                return

            title = " ".join(context.args)

            @sync_to_async
            def create_idea_instance(user, title):
                from idea.models import Myidea
                # Создаем идею без проблемных полей
                return Myidea.objects.create(
                    owner=user,
                    title=title,
                    is_public=True
                )

            idea = await create_idea_instance(user, title)

            # Публикация в Telegram
            telegram_service = TelegramService()
            author_name = user.first_name or user.email.split('@')[0]
            message = f"💡 Новая идея!\n\nИдея: {idea.title}\nАвтор: {author_name}"
            telegram_service.send_to_topic('ideas', message, True)

            await update.message.reply_text(f"✅ Идея создана: {idea.title}")

        except Exception as e:
            logger.error(f"Idea creation error: {e}")
            await update.message.reply_text("❌ Ошибка при создании идеи")

    async def create_moment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание момента - УПРОЩЕННАЯ ВЕРСИЯ"""
        try:
            user = await self.get_django_user(update, context)
            if not user:
                await update.message.reply_text("❌ Пользователь не найден. Используйте /start для регистрации")
                return

            if not context.args:
                await update.message.reply_text(
                    "📸 Введите название момента после команды:\n"
                    "Пример: /create_moment Прогулка в парке"
                )
                return

            title = " ".join(context.args)

            @sync_to_async
            def create_moment_instance(user, title):
                from moments.models import Moment
                # Создаем момент без проблемных полей
                return Moment.objects.create(
                    owner=user,
                    title=title,
                    is_public=False,
                    comments="Момент создан через бота",  # Обязательное поле
                    event_date=timezone.now()  # Обязательное поле
                )

            moment = await create_moment_instance(user, title)

            # Публикация в Telegram
            telegram_service = TelegramService()
            author_name = user.first_name or user.email.split('@')[0]
            message = f"📸 Новый момент!\n\nМомент: {moment.title}\nАвтор: {author_name}"
            telegram_service.send_to_topic('moments', message, True)

            await update.message.reply_text(f"✅ Момент создан: {moment.title}")

        except Exception as e:
            logger.error(f"Moment creation error: {e}")
            await update.message.reply_text("❌ Ошибка при создании момента")

    # ===== МЕТОДЫ ПОКАЗА ЗАПИСЕЙ =====

    async def show_habits(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ привычек пользователя - УПРОЩЕННАЯ ВЕРСИЯ"""
        try:
            user = await self.get_django_user(update, context)
            if not user:
                await update.message.reply_text("❌ Пользователь не найден. Используйте /start для регистрации")
                return

            @sync_to_async
            def get_user_habits(user):
                from habits.models import Habit
                try:
                    # Используем только безопасные поля
                    return list(Habit.objects.filter(owner=user, is_active=True))
                except Exception as e:
                    logger.error(f"Database error in get_user_habits: {e}")
                    return []

            habits = await get_user_habits(user)

            if not habits:
                await update.message.reply_text("📝 У вас пока нет привычек.\nИспользуйте /create_habit <действие>")
                return

            text = "📋 Ваши привычки:\n\n"
            for habit in habits:
                # Используем getattr для безопасного доступа
                is_public = getattr(habit, 'is_public', False)
                public_icon = "🔓" if is_public else "🔒"

                text += f"{public_icon} {habit.action}\n"

                comments = getattr(habit, 'comments', None)
                if comments:
                    text += f"   📝 {comments}\n"

                time_deadline = getattr(habit, 'time_deadline', None)
                if time_deadline:
                    text += f"   🕐 {time_deadline.strftime('%H:%M')} | "

                periodicity = getattr(habit, 'periodicity', 1)
                text += f"📅 каждые {periodicity} дней\n"

                location = getattr(habit, 'location', 'Не указано')
                text += f"   📍 {location}\n\n"

            await update.message.reply_text(text)

        except Exception as e:
            logger.error(f"Error showing habits: {e}")
            await update.message.reply_text("❌ Ошибка при получении привычек")

    async def show_goals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ целей пользователя - УПРОЩЕННАЯ ВЕРСИЯ"""
        try:
            user = await self.get_django_user(update, context)
            if not user:
                await update.message.reply_text("❌ Пользователь не найден. Используйте /start для регистрации")
                return

            @sync_to_async
            def get_user_goals(user):
                from goal.models import Goal
                try:
                    # Используем только безопасные поля
                    return list(Goal.objects.filter(owner=user, is_active=True))
                except Exception as e:
                    logger.error(f"Database error in get_user_goals: {e}")
                    return []

            goals = await get_user_goals(user)

            if not goals:
                await update.message.reply_text("🎯 У вас пока нет целей.\nИспользуйте /create_goal <название>")
                return

            text = "🎯 Ваши цели:\n\n"
            for goal in goals:
                # Используем getattr для безопасного доступа
                is_public = getattr(goal, 'is_public', False)
                public_icon = "🔓" if is_public else "🔒"
                text += f"{public_icon} {goal.title}\n"

                comments = getattr(goal, 'comments', None)
                if comments:
                    text += f"   📝 {comments}\n"

                date_deadline = getattr(goal, 'date_deadline', None)
                if date_deadline:
                    text += f"   📅 Срок: {date_deadline.strftime('%d.%m.%Y')}\n"
                text += "\n"

            await update.message.reply_text(text)

        except Exception as e:
            logger.error(f"Error showing goals: {e}")
            await update.message.reply_text("❌ Ошибка при получении целей")

    async def show_ideas(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ идей пользователя - УПРОЩЕННАЯ ВЕРСИЯ"""
        try:
            user = await self.get_django_user(update, context)
            if not user:
                await update.message.reply_text("❌ Пользователь не найден. Используйте /start для регистрации")
                return

            @sync_to_async
            def get_user_ideas(user):
                from idea.models import Myidea
                try:
                    return list(Myidea.objects.filter(owner=user))
                except Exception as e:
                    logger.error(f"Database error in get_user_ideas: {e}")
                    return []

            ideas = await get_user_ideas(user)

            if not ideas:
                await update.message.reply_text("💡 У вас пока нет идей.\nИспользуйте /create_idea <название>")
                return

            text = "💡 Ваши идеи:\n\n"
            for idea in ideas:
                # Используем getattr для безопасного доступа
                is_public = getattr(idea, 'is_public', False)
                public_icon = "🔓" if is_public else "🔒"
                text += f"{public_icon} {idea.title}\n"

                comments = getattr(idea, 'comments', None)
                if comments:
                    text += f"   📝 {comments}\n"
                text += "\n"

            await update.message.reply_text(text)

        except Exception as e:
            logger.error(f"Error showing ideas: {e}")
            await update.message.reply_text("❌ Ошибка при получении идей")

    async def show_moments(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ моментов пользователя - УПРОЩЕННАЯ ВЕРСИЯ"""
        try:
            user = await self.get_django_user(update, context)
            if not user:
                await update.message.reply_text("❌ Пользователь не найден. Используйте /start для регистрации")
                return

            @sync_to_async
            def get_user_moments(user):
                from moments.models import Moment
                try:
                    return list(Moment.objects.filter(owner=user))
                except Exception as e:
                    logger.error(f"Database error in get_user_moments: {e}")
                    return []

            moments = await get_user_moments(user)

            if not moments:
                await update.message.reply_text("📸 У вас пока нет моментов.\nИспользуйте /create_moment <название>")
                return

            text = "📸 Ваши моменты:\n\n"
            for moment in moments:
                # Используем getattr для безопасного доступа
                is_public = getattr(moment, 'is_public', False)
                public_icon = "🔓" if is_public else "🔒"
                text += f"{public_icon} {moment.title}\n"

                comments = getattr(moment, 'comments', None)
                if comments:
                    text += f"   📝 {comments}\n"

                location = getattr(moment, 'location', None)
                if location:
                    text += f"   📍 {location}\n"
                text += "\n"

            await update.message.reply_text(text)

        except Exception as e:
            logger.error(f"Error showing moments: {e}")
            await update.message.reply_text("❌ Ошибка при получении моментов")

    async def public_feed(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ публичной ленты - УПРОЩЕННАЯ ВЕРСИЯ"""
        try:
            @sync_to_async
            def get_public_content():
                try:
                    from habits.models import Habit
                    from goal.models import Goal
                    from moments.models import Moment
                    from idea.models import Myidea

                    # Безопасные запросы
                    public_habits = list(Habit.objects.filter(is_public=True, is_active=True)[:5])
                    public_goals = list(Goal.objects.filter(is_public=True, is_active=True)[:5])
                    public_ideas = list(Myidea.objects.filter(is_public=True)[:5])
                    public_moments = list(Moment.objects.filter(is_public=True)[:5])

                    return public_habits, public_goals, public_ideas, public_moments
                except Exception as e:
                    logger.error(f"Database error in get_public_content: {e}")
                    return [], [], [], []

            public_habits, public_goals, public_ideas, public_moments = await get_public_content()

            text = "🌟 Публичная лента\n\n"

            if public_habits:
                text += "📋 Публичные привычки:\n"
                for habit in public_habits:
                    text += f"• {habit.action}"
                    comments = getattr(habit, 'comments', None)
                    if comments:
                        text += f" - {comments}"
                    text += "\n"
                text += "\n"

            if public_goals:
                text += "🎯 Публичные цели:\n"
                for goal in public_goals:
                    text += f"• {goal.title}"
                    comments = getattr(goal, 'comments', None)
                    if comments:
                        text += f" - {comments}"
                    text += "\n"
                text += "\n"

            if public_ideas:
                text += "💡 Публичные идеи:\n"
                for idea in public_ideas:
                    text += f"• {idea.title}"
                    comments = getattr(idea, 'comments', None)
                    if comments:
                        text += f" - {comments}"
                    text += "\n"
                text += "\n"

            if public_moments:
                text += "📸 Публичные моменты:\n"
                for moment in public_moments:
                    text += f"• {moment.title}"
                    comments = getattr(moment, 'comments', None)
                    if comments:
                        text += f" - {comments}"
                    text += "\n"

            if not any([public_habits, public_goals, public_ideas, public_moments]):
                text += "😔 В публичной ленте пока пусто.\nСоздайте публичные записи!"

            await update.message.reply_text(text)

        except Exception as e:
            logger.error(f"Error showing public feed: {e}")
            await update.message.reply_text("❌ Ошибка при получении публичной ленты")

    # ===== ОСНОВНЫЕ КОМАНДЫ =====

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда start - с автоматической регистрацией"""
        # Автоматически регистрируем пользователя
        user = await self.get_django_user(update, context)

        if user:
            author_name = user.first_name or user.email.split('@')[0]
            welcome_text = f"""
🤖 Привет, {author_name}!

✅ Вы успешно зарегистрированы в LifeCanvas Diary Bot!

📋 Основные команды:
/habits - Мои привычки  
/goals - Мои цели
/ideas - Мои идеи
/moments - Мои моменты
/public_feed - Публичная лента

✨ Создание записей:
/create_habit <действие> - Новая привычка
/create_goal <название> - Новая цель
/create_idea <название> - Новая идея  
/create_moment <название> - Новый момент

💡 Примеры:
/create_habit читать книгу 30 минут
/create_goal Выучить Python за 3 месяца
/create_idea Приложение для трекинга привычек
/create_moment Прогулка в парке

🆔 Ваш ID: {user.chat_id}
            """
        else:
            welcome_text = """
🤖 Привет!

Добро пожаловать в LifeCanvas Diary Bot!

⚠️ Не удалось автоматически зарегистрировать вас.
Пожалуйста, свяжитесь с администратором.
            """

        await update.message.reply_text(welcome_text)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда help"""
        help_text = """
📋 Доступные команды:

👀 Просмотр записей:
/habits - Мои привычки  
/goals - Мои цели
/ideas - Мои идеи
/moments - Мои моменты
/public_feed - Публичная лента

➕ Создание записей:
/create_habit <действие> - Создать привычку
/create_goal <название> - Создать цель
/create_idea <название> - Создать идею  
/create_moment <название> - Создать момент

🔧 Другие команды:
/start - Начать работу
/channels - Информация о темах
/help - Помощь
        """
        await update.message.reply_text(help_text)

    async def register(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда register"""
        user = await self.get_django_user(update, context)
        if user:
            author_name = user.first_name or user.email.split('@')[0]
            await update.message.reply_text(
                f"✅ Вы уже зарегистрированы!\n\n"
                f"👤 Имя: {author_name}\n"
                f"📧 Email: {user.email}\n"
                f"🆔 Telegram ID: {user.chat_id}"
            )
        else:
            await update.message.reply_text("❌ Не удалось зарегистрировать. Попробуйте /start")

    async def channels_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Информация о каналах"""
        text = """
📢 Информация о темах

🔓 Публичные темы:
• 📋 Привычки - смотрите публичные привычки
• 🎯 Цели - смотрите публичные цели
• 💡 Идеи - смотрите публичные идеи
• 📸 Моменты - смотрите публичные моменты

🔒 Приватные темы:
• 📋 Мои привычки - ваши приватные привычки
• 🎯 Мои цели - ваши приватные цели
• 💡 Мои идеи - ваши приватные идеи
• 📸 Мои моменты - ваши приватные моменты

💡 Записи создаются автоматически в соответствующие темы
        """
        await update.message.reply_text(text)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик обычных сообщений"""
        await update.message.reply_text(
            "Используйте команды для работы с дневником.\n"
            "Напишите /help для списка команд."
        )

    def run(self):
        """Запуск бота"""
        print("🔄 Бот запускается...")
        try:
            self.application.run_polling()
        except KeyboardInterrupt:
            print("✅ Бот остановлен")
        except Exception as e:
            print(f"❌ Ошибка: {e}")


async def make_public(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сделать запись публичной"""
    try:
        # Получаем пользователя
        user = await self.get_django_user(update, context)
        if not user:
            await update.message.reply_text("❌ Пользователь не найден")
            return

        if not context.args:
            await update.message.reply_text(
                "🔓 Сделать запись публичной\n\n"
                "Использование: /make_public <тип> <id>\n"
                "Типы: habit, goal, idea, moment\n\n"
                "Пример: /make_public habit 1\n"
                "Пример: /make_public goal 1"
            )
            return

        if len(context.args) < 2:
            await update.message.reply_text("❌ Укажите тип записи и ID")
            return

        content_type = context.args[0].lower()
        record_id = context.args[1]

        @sync_to_async
        def set_public(content_type, record_id):
            try:
                if content_type == 'habit':
                    from habits.models import Habit
                    record = Habit.objects.get(id=record_id, owner=user)
                elif content_type == 'goal':
                    from goal.models import Goal
                    record = Goal.objects.get(id=record_id, owner=user)
                elif content_type == 'idea':
                    from idea.models import Myidea
                    record = Myidea.objects.get(id=record_id, owner=user)
                elif content_type == 'moment':
                    from moments.models import Moment
                    record = Moment.objects.get(id=record_id, owner=user)
                else:
                    return None

                record.is_public = True
                record.save()
                return record
            except Exception as e:
                logger.error(f"Error making {content_type} public: {e}")
                return None

        record = await set_public(content_type, record_id)

        if record:
            await update.message.reply_text(f"✅ Запись #{record_id} ({content_type}) теперь публичная")
        else:
            await update.message.reply_text("❌ Не удалось сделать запись публичной")

    except Exception as e:
        logger.error(f"Error in make_public: {e}")
        await update.message.reply_text("❌ Ошибка")

if __name__ == "__main__":
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    bot = TelegramBot()
    bot.run()
