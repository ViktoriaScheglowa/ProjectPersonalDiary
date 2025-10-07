from django import forms
from django.contrib.auth.forms import UserCreationForm

from moments.forms import StyleFormMixin
from .models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    """Класс создания формы регистрации пользователя"""
    phone_number = forms.CharField(max_length=15, required=False,
                                   help_text='Необязательное поле. Введите ваш номер телефона.')
    email = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
