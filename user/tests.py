import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class TestUserAPI:
    """Тесты для API пользователей"""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            email="apiuser@example.com", password="testpass123"
        )

    @pytest.fixture
    def user_detail_url(self, user):
        return f"/api/users/{user.id}/"

    @pytest.mark.django_db
    def test_user_retrieve_requires_auth(self, api_client, user_detail_url):
        """Тест что получение пользователя требует авторизации"""
        response = api_client.get(user_detail_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_user_retrieve(self, api_client, user, user_detail_url):
        """Тест получения информации о пользователе"""
        api_client.force_authenticate(user=user)
        response = api_client.get(user_detail_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    @pytest.mark.django_db
    def test_user_update(self, api_client, user, user_detail_url):
        """Тест обновления пользователя"""
        api_client.force_authenticate(user=user)

        data = {"phone_number": "+79991112233", "country": "Germany"}

        response = api_client.patch(user_detail_url, data)

        user.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert user.phone_number == data["phone_number"]
        assert user.country == data["country"]

    @pytest.mark.django_db
    def test_user_delete(self, api_client, user, user_detail_url):
        """Тест удаления пользователя"""
        api_client.force_authenticate(user=user)

        response = api_client.delete(user_detail_url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(id=user.id).exists()
