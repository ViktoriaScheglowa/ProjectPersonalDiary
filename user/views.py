from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
import secrets

from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, UpdateView, ListView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from config import settings
from config.settings import EMAIL_HOST_USER
from user.forms import UserRegisterForm, UserProfileForm
from user.models import User
from user.serializers import UserRegisterSerializer, UserPublicSerializer, UserSerializers


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'user/register.html'
    success_url = reverse_lazy('main')

    def form_valid(self, form):
        try:
            # Сохраняем пользователя
            user = form.save(commit=False)
            user.is_active = False
            token = secrets.token_hex(16)
            user.token = token

            # Сохраняем в базу
            user.save()

            # Отправляем email
            host = self.request.get_host()
            url = f"http://{host}/user/email-confirm/{token}/"

            # Для отладки выведем ссылку в консоль
            print(f"Ссылка для подтверждения: {url}")

            try:
                send_mail(
                    subject="Добро пожаловать в наш сервис",
                    message=f"Чтобы подтвердить почту, перейдите по ссылке {url}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email]
                )
                print(f"Email отправлен на {user.email}")
            except Exception as e:
                print(f"Ошибка отправки email: {e}")
                # Сохраняем пользователя даже если email не отправился
                pass

            messages.success(self.request, 'Регистрация успешна! Проверьте email для подтверждения.')
            return super().form_valid(form)

        except Exception as e:
            print(f"Ошибка при регистрации: {e}")
            messages.error(self.request, f'Ошибка регистрации: {e}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        print("Форма невалидна. Ошибки:")
        for field, errors in form.errors.items():
            print(f"{field}: {errors}")
        return super().form_invalid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.token = ''
    user.save()
    messages.success(request, 'Email успешно подтвержден! Теперь вы можете войти.')
    return redirect("user:login")


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'user/profile.html'
    success_url = reverse_lazy('main')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'user/user_list.html'
    context_object_name = 'users'


# class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
#     """Сериализатор для входа по email вместо username"""
#
#     def validate(self, attrs):
#         email = attrs.get('email')
#         password = attrs.get('password')
#
#         if email and password:
#             try:
#                 user = User.objects.get(email=email)
#                 attrs['username'] = user.email
#             except User.DoesNotExist:
#                 pass
#
#         return super().validate(attrs)
#
#
# class LoginView(TokenObtainPairView):
#     """View для входа с поддержкой HTML формы"""
#     serializer_class = EmailTokenObtainPairSerializer
#     permission_classes = (AllowAny,)
#
#     def get(self, request, *args, **kwargs):
#         return render(request, 'user/login.html')
#
#
# class UserCreateAPIView(CreateAPIView):
#     """View для регистрации пользователя"""
#     serializer_class = UserRegisterSerializer
#     queryset = User.objects.all()
#     permission_classes = (AllowAny,)
#
#     def get(self, request, *args, **kwargs):
#         """Отображает форму регистрации"""
#         return render(request, 'user/register.html')
#
#     def post(self, request, *args, **kwargs):
#         """Обрабатывает регистрацию через форму или API"""
#         if self._is_html_form(request):
#             return self._handle_form_submission(request)
#         return super().post(request, *args, **kwargs)
#
#     def _is_html_form(self, request):
#         """Проверяет, является ли запрос HTML формой"""
#         return request.content_type == 'application/x-www-form-urlencoded'
#
#     def _handle_form_submission(self, request):
#         """Обрабатывает отправку HTML формы"""
#         data = {
#             'email': request.POST.get('email'),
#             'password': request.POST.get('password')
#         }
#
#         serializer = self.get_serializer(data=data)
#         if serializer.is_valid():
#             self.perform_create(serializer)
#             context = {'success_message': 'Регистрация успешна! Проверьте email для подтверждения.'}
#         else:
#             context = {
#                 'error_message': 'Ошибка регистрации. Проверьте данные.',
#                 'form_data': data,
#                 'errors': serializer.errors
#             }
#
#         return render(request, 'user/register.html', context)
#
#     def perform_create(self, serializer):
#         """Создает пользователя и отправляет email подтверждения"""
#         user = serializer.save(is_active=False)
#         user.set_password(serializer.validated_data['password'])
#
#         token = secrets.token_hex(16)
#         user.token = token
#         user.save()
#
#         self._send_confirmation_email(user, token)
#
#     def _send_confirmation_email(self, user, token):
#         """Отправляет email с ссылкой подтверждения"""
#         host = self.request.get_host()
#         url = f"http://{host}/user/email-confirm/{token}"
#
#         send_mail(
#             subject="Добро пожаловать в наш сервис",
#             message=f"Чтобы подтвердить почту, перейдите по ссылке {url}",
#             from_email=EMAIL_HOST_USER,
#             recipient_list=[user.email]
#         )
#
#
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def email_verification(request, token):
#     """Подтверждение email пользователя"""
#     user = get_object_or_404(User, token=token)
#     user.is_active = True
#     user.token = None
#     user.save()
#
#     return render(request, 'user/email_confirmation_success.html')
#
#
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def logout_view(request):
#     """Выход пользователя"""
#     return Response({"detail": "Успешный выход"}, status=status.HTTP_200_OK)
#
#
# class UserListAPIView(ListAPIView):
#     """Список пользователей"""
#     serializer_class = UserPublicSerializer
#     queryset = User.objects.all()
#     permission_classes = (IsAuthenticated,)
class UserRetrieveAPIView(RetrieveAPIView):
    """Детальная информация о пользователе"""
    serializer_class = UserSerializers
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)


class UserUpdateAPIView(UpdateAPIView):
    """Обновление пользователя"""
    serializer_class = UserSerializers
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)


class UserDestroyAPIView(DestroyAPIView):
    """Удаление пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializers
    permission_classes = (IsAuthenticated,)


@method_decorator(csrf_protect, name='dispatch')
class CustomLoginView(View):
    template_name = 'user/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('main')
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('username')
        password = request.POST.get('password')

        print(f"Попытка входа с email: {email}")

        # Аутентифицируем пользователя
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.email}!')
                print(f"Успешный вход для пользователя: {user.email}")
                return redirect('main')
            else:
                messages.error(request, 'Ваш аккаунт не активирован. Проверьте email для подтверждения.')
                print("Вход не удался: аккаунт не активен")
        else:
            messages.error(request, 'Неверный email или пароль.')
            print("Вход не удался: неверные учетные данные")

        return render(request, self.template_name)
