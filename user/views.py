from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
import secrets
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    DestroyAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    ListAPIView,
    CreateAPIView,
)
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from config.settings import EMAIL_HOST_USER
from user.forms import UserRegisterForm
from user.models import User
from user.serializers import (
    UserRegisterSerializer,
    UserPublicSerializer,
    UserSerializers,
)

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Позволяет входить по email вместо username
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            try:
                username = User.objects.get(email=email).username
                attrs['username'] = username
            except User.DoesNotExist:
                pass

        return super().validate(attrs)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def get(self, request, *args, **kwargs):
        return render(request, 'user/login.html')


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="Создание пользователя",
        operation_description="Создание нового пользователя. Для авторизации требуются email и пароль.",
    ),
)
@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Форма регистрации",
        operation_description="Отображает форму для регистрации нового пользователя",
        responses={200: "HTML форма регистрации"}
    ),
)
class UserCreateAPIView(CreateAPIView):
    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        """Отображает HTML-форму регистрации"""
        return render(request, 'user/register.html')

    def post(self, request, *args, **kwargs):
        # Если это форма (обычный POST), обрабатываем как форму
        if request.content_type == 'application/x-www-form-urlencoded':
            # Создаем данные для сериализатора
            data = {
                'username': request.POST.get('username'),
                'email': request.POST.get('email'),
                'password': request.POST.get('password')
            }

            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)
                return render(request, 'user/register.html', {
                    'success_message': 'Регистрация успешна! Проверьте email для подтверждения.'
                })
            else:
                return render(request, 'user/register.html', {
                    'error_message': 'Ошибка регистрации. Проверьте данные.',
                    'form_data': data,
                    'errors': serializer.errors
                })

        # Иначе используем стандартное API поведение
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = serializer.save(is_active=False)
        user.set_password(serializer.validated_data['password'])
        token = secrets.token_hex(16)
        user.token = token
        user.save()

        host = self.request.get_host()
        url = f"http://{host}/user/email-confirm/{token}"  # Убедитесь, что здесь 'user', а не 'users'
        send_mail(
            subject="Добро пожаловать в наш сервис",
            message=f"Чтобы подтвердить почту, перейдите по ссылке {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email]
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.token = None
    user.save()

    return render(request, 'user/email_confirmation_success.html')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # Просто возвращаем успешный ответ - клиент удаляет токены
    response = Response({"detail": "Успешный выход"}, status=status.HTTP_200_OK)
    return response


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Список пользователей",
        operation_description="Вывод списка авторизованных пользователей. "
                              "Требуется авторизация. Для просмотра доступны "
        "поля: email, имя, город, аватар.",
        responses={200: UserPublicSerializer(many=True)},
    ),
)
class UserListAPIView(ListAPIView):
    serializer_class = UserPublicSerializer
    queryset = User.objects.all()


class UserRetrieveAPIView(LoginRequiredMixin, RetrieveAPIView):
    serializer_class = UserSerializers
    queryset = User.objects.all()

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        else:
            raise PermissionDenied


class UserUpdateAPIView(UpdateAPIView):
    serializer_class = UserSerializers
    queryset = User.objects.all()


class UserDestroyAPIView(DestroyAPIView):
    queryset = User.objects.all()


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)
