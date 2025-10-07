from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from user.apps import UserConfig
from user.views import (
    UserListAPIView,
    UserCreateAPIView,
    UserRetrieveAPIView,
    UserUpdateAPIView,
    UserDestroyAPIView, email_verification, logout_view,
)

app_name = UserConfig.name


class LoginView(TokenObtainPairView):
    def get(self, request, *args, **kwargs):
        from django.shortcuts import render
        return render(request, 'user/login.html')


urlpatterns = [
    path("", UserListAPIView.as_view(), name="user-list"),
    path("register/", UserCreateAPIView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("<int:pk>/", UserRetrieveAPIView.as_view(), name="user-detail"),
    path("<int:pk>/update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("<int:pk>/delete/", UserDestroyAPIView.as_view(), name="user-delete"),
    path("email-confirm/<str:token>/", email_verification, name='email_confirm'),
]
