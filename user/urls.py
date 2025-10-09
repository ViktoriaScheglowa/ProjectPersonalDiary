from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)

from .apps import UserConfig
from django.contrib.auth import views as auth_views
from .views import (
    UserListView, UserCreateView, UserProfileUpdateView,
    UserRetrieveAPIView, UserUpdateAPIView, UserDestroyAPIView, email_verification, CustomLoginView
)
from .forms import CustomSetPasswordForm

app_name = UserConfig.name

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page='/'), name="logout"),
    path('profile/', UserProfileUpdateView.as_view(), name='profile'),
    path('user_list/', UserListView.as_view(), name='user_list'),
    path("email-confirm/<str:token>/", email_verification, name='email_confirm'),

    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='user/password_reset_form.html',
             email_template_name='user/password_reset_email.html',
             subject_template_name='user/password_reset_subject.txt',
             success_url='/user/password-reset/done/'
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='user/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='user/password_reset_confirm.html',
             success_url='/user/password-reset/complete/'
         ),
         name='password_reset_confirm'),

    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='user/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    path("<int:pk>/", UserRetrieveAPIView.as_view(), name="user-detail"),
    path("<int:pk>/update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("<int:pk>/delete/", UserDestroyAPIView.as_view(), name="user-delete"),
]
