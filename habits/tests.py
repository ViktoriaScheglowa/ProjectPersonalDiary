import datetime
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from habits.models import Habit

User = get_user_model()


class HabitCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(
            email="test1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create(
            email="test2@example.com", password="testpass123"
        )

        self.habit1 = Habit.objects.create(
            owner=self.user1,
            location="Test Location",
            action="Test action 1",
            time_deadline=datetime.time(10, 30),
            date_deadline=timezone.now().date() + datetime.timedelta(days=7),
            is_enjoyable=False,
            is_public=True,
            periodicity=1,
        )

        self.habit2 = Habit.objects.create(
            owner=self.user2,
            location="Test Location 2",
            action="Test action 2",
            time_deadline=datetime.time(14, 45),
            date_deadline=timezone.now().date() + datetime.timedelta(days=7),
            is_enjoyable=False,
            is_public=False,
            periodicity=1,
        )

    def test_requires_login(self):
        """Тест что создание привычки требует аутентификации"""
        response = self.client.get(reverse("habits:habits_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/user/login/", response.url)

    def test_get_create_view(self):
        """Тест GET запроса к форме создания"""
        self.client.force_login(self.user1)
        response = self.client.get(reverse("habits:habits_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "habits/habits_form.html")

    def test_post_create_view_valid_data(self):
        """Тест POST запроса с валидными данными"""
        self.client.force_login(self.user1)

        # Создаем данные только с теми полями, которые есть в форме HabitForm
        data = {
            "location": "New Location",
            "action": "New action",
            "time_deadline": "09:00:00",
            "date_deadline": (
                timezone.now().date() + datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d"),
            "periodicity": 1,
            "is_public": True,  # Это поле есть в форме
            # is_enjoyable НЕ включаем, так как его нет в форме HabitForm
        }

        response = self.client.post(reverse("habits:habits_create"), data)

        # Проверяем редирект при успешном создании
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("habits:habits_list"))

        # Проверяем, что привычка действительно создалась
        self.assertEqual(Habit.objects.count(), 3)

        # Дополнительная проверка - убедимся, что созданная привычка принадлежит текущему пользователю
        new_habit = Habit.objects.latest("id")
        self.assertEqual(new_habit.owner, self.user1)
        self.assertEqual(new_habit.location, "New Location")
        self.assertEqual(new_habit.periodicity, 1)
        self.assertEqual(new_habit.is_public, True)
        # is_enjoyable должно быть установлено в значение по умолчанию (False)


class HabitListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(
            email="test1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create(
            email="test2@example.com", password="testpass123"
        )

        self.habit1 = Habit.objects.create(
            owner=self.user1,
            location="Test Location",
            action="Test action 1",
            time_deadline=datetime.time(10, 30),
            date_deadline=timezone.now().date() + datetime.timedelta(days=7),
            is_enjoyable=False,
            is_public=True,
            periodicity=1,
        )

        self.habit2 = Habit.objects.create(
            owner=self.user2,
            location="Test Location 2",
            action="Test action 2",
            time_deadline=datetime.time(14, 45),
            date_deadline=timezone.now().date() + datetime.timedelta(days=7),
            is_enjoyable=False,
            is_public=False,
            periodicity=1,
        )

    def test_requires_login(self):
        """Тест что представление требует аутентификации"""
        response = self.client.get(reverse("habits:habits_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/user/login/", response.url)

    def test_authenticated_access(self):
        """Тест доступа аутентифицированного пользователя"""
        self.client.force_login(self.user1)
        response = self.client.get(reverse("habits:habits_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "habits/my_habits_list.html")

    def test_context_contains_user_habits(self):
        """Тест что контекст содержит только привычки текущего пользователя"""
        self.client.force_login(self.user1)
        response = self.client.get(reverse("habits:habits_list"))

        habits_in_context = list(response.context["habits"])
        user_habits = list(Habit.objects.filter(owner=self.user1))

        self.assertEqual(len(habits_in_context), len(user_habits))
        self.assertTrue(all(habit.owner == self.user1 for habit in habits_in_context))


class HabitDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(
            email="test1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create(
            email="test2@example.com", password="testpass123"
        )

        self.habit1 = Habit.objects.create(
            owner=self.user1,
            location="Test Location",
            action="Test action 1",
            time_deadline=datetime.time(10, 30),
            date_deadline=timezone.now().date() + datetime.timedelta(days=7),
            is_enjoyable=False,
            is_public=True,
            periodicity=1,
        )

        self.habit2 = Habit.objects.create(
            owner=self.user2,
            location="Test Location 2",
            action="Test action 2",
            time_deadline=datetime.time(14, 45),
            date_deadline=timezone.now().date() + datetime.timedelta(days=7),
            is_enjoyable=False,
            is_public=False,
            periodicity=1,
        )

    def test_requires_login(self):
        """Тест что просмотр деталей требует аутентификации"""
        response = self.client.get(
            reverse("habits:habits_detail", args=[self.habit1.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/user/login/", response.url)

    def test_view_own_habit(self):
        """Тест просмотра своей привычки"""
        self.client.force_login(self.user1)
        response = self.client.get(
            reverse("habits:habits_detail", args=[self.habit1.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "habits/habits_detail.html")
        self.assertEqual(response.context["habit"], self.habit1)

    def test_cannot_view_private_other_user_habit(self):
        """Тест что нельзя просматривать приватные привычки других пользователей"""
        self.client.force_login(self.user1)
        response = self.client.get(
            reverse("habits:habits_detail", args=[self.habit2.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_view_public_other_user_habit(self):
        """Тест что можно просматривать публичные привычки других пользователей"""
        public_habit = Habit.objects.create(
            owner=self.user2,
            location="Public Location",
            action="Public action",
            time_deadline=datetime.time(16, 0),
            date_deadline=timezone.now().date() + datetime.timedelta(days=7),
            is_enjoyable=False,
            is_public=True,
            periodicity=1,
        )

        self.client.force_login(self.user1)
        response = self.client.get(
            reverse("habits:habits_detail", args=[public_habit.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["habit"], public_habit)


class HabitUpdateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(
            email="test1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create(
            email="test2@example.com", password="testpass123"
        )

        self.habit1 = Habit.objects.create(
            owner=self.user1,
            location="Test Location",
            action="Test action 1",
            time_deadline=datetime.time(10, 30),
            date_deadline=timezone.now().date() + datetime.timedelta(days=7),
            is_enjoyable=False,
            is_public=True,
            periodicity=1,
        )

        self.habit2 = Habit.objects.create(
            owner=self.user2,
            location="Test Location 2",
            action="Test action 2",
            time_deadline=datetime.time(14, 45),
            date_deadline=timezone.now().date() + datetime.timedelta(days=7),
            is_enjoyable=False,
            is_public=False,
            periodicity=1,
        )

    def test_requires_login(self):
        """Тест что обновление требует аутентификации"""
        response = self.client.get(
            reverse("habits:habits_update", args=[self.habit1.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/user/login/", response.url)

    def test_get_update_own_habit(self):
        """Тест GET запроса для своей привычки"""
        self.client.force_login(self.user1)
        response = self.client.get(
            reverse("habits:habits_update", args=[self.habit1.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "habits/habits_form.html")

    def test_cannot_update_other_user_habit(self):
        """Тест что нельзя обновить чужую привычку"""
        self.client.force_login(self.user1)
        response = self.client.get(
            reverse("habits:habits_update", args=[self.habit2.id])
        )
        self.assertEqual(response.status_code, 404)


class HabitDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(
            email="test1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create(
            email="test2@example.com", password="testpass123"
        )

        self.habit1 = Habit.objects.create(
            owner=self.user1,
            location="Test Location",
            action="Test action 1",
            time_deadline=datetime.time(10, 30),
            date_deadline=timezone.now().date() + datetime.timedelta(days=7),
            is_enjoyable=False,
            is_public=True,
            periodicity=1,
        )

        self.habit2 = Habit.objects.create(
            owner=self.user2,
            location="Test Location 2",
            action="Test action 2",
            time_deadline=datetime.time(14, 45),
            date_deadline=timezone.now().date() + datetime.timedelta(days=7),
            is_enjoyable=False,
            is_public=False,
            periodicity=1,
        )

    def test_requires_login(self):
        """Тест что удаление требует аутентификации"""
        response = self.client.get(
            reverse("habits:habits_delete", args=[self.habit1.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/user/login/", response.url)

    def test_get_delete_own_habit(self):
        """Тест GET запроса для подтверждения удаления своей привычки"""
        self.client.force_login(self.user1)
        response = self.client.get(
            reverse("habits:habits_delete", args=[self.habit1.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "habits/habits_confirm_delete.html")

    def test_post_delete_own_habit(self):
        """Тест POST запроса для удаления своей привычки"""
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse("habits:habits_delete", args=[self.habit1.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("habits:habits_list"))
        self.assertEqual(Habit.objects.count(), 1)

    def test_cannot_delete_other_user_habit(self):
        """Тест что нельзя удалить чужую привычку"""
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse("habits:habits_delete", args=[self.habit2.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Habit.objects.count(), 2)


class PublicHabitsTemplateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(
            email="test1@example.com", password="testpass123"
        )

        self.habit1 = Habit.objects.create(
            owner=self.user1,
            location="Test Location",
            action="Test action 1",
            time_deadline=datetime.time(10, 30),
            date_deadline=timezone.now().date() + datetime.timedelta(days=7),
            is_enjoyable=False,
            is_public=True,
            periodicity=1,
        )

        self.habit2 = Habit.objects.create(
            owner=self.user1,
            location="Test Location 2",
            action="Test action 2",
            time_deadline=datetime.time(14, 45),
            date_deadline=timezone.now().date() + datetime.timedelta(days=7),
            is_enjoyable=False,
            is_public=False,
            periodicity=1,
        )

    def test_public_habits_context(self):
        """Тест что в контекст передаются только публичные привычки"""
        response = self.client.get(reverse("habits:public_habits_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "habits/public_habits_list.html")

        public_habits = response.context["habits"]
        self.assertEqual(len(public_habits), 1)
        self.assertEqual(public_habits[0], self.habit1)
