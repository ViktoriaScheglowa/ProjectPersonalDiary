# idea/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Myidea

User = get_user_model()


class SimpleMyideaTest(TestCase):
    """Простой тест без создания пользователей через менеджер"""

    def test_idea_basic_functionality(self):
        """Базовый тест функциональности Myidea"""
        # Создаем пользователя напрямую
        user = User.objects.create(email="test@example.com")
        user.set_password("testpass123")
        user.save()

        # Создаем идею
        idea = Myidea.objects.create(
            title="Test Idea", comments="Test comments", owner=user
        )

        self.assertEqual(idea.title, "Test Idea")
        self.assertEqual(idea.owner, user)
        self.assertIsNotNone(idea.created_at)
