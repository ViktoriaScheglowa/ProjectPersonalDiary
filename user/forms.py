from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm

from .models import User


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if hasattr(field, 'widget') and hasattr(field.widget, 'attrs'):
                if 'class' not in field.widget.attrs:
                    if isinstance(field, forms.BooleanField):
                        field.widget.attrs['class'] = 'form-check-input'
                    else:
                        field.widget.attrs['class'] = 'form-control'


class UserRegisterForm(forms.ModelForm):
    """
    Кастомная форма регистрации для модели User без username
    """
    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        }),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        }),
        strip=False,
        help_text="Введите тот же пароль еще раз для проверки.",
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию'
            }),
        }
        labels = {
            'email': 'Email адрес',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error("password2", error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'avatar', 'phone_number', 'country', 'chat_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        self.fields['first_name'].widget.attrs['placeholder'] = 'Введите имя'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Введите фамилию'
        self.fields['email'].widget.attrs['placeholder'] = 'Введите почту'
        self.fields['phone_number'].widget.attrs['placeholder'] = '+7 (XXX) XXX-XX-XX'
        self.fields['country'].widget.attrs['placeholder'] = 'Страна проживания'
        self.fields['chat_id'].widget.attrs['placeholder'] = 'ID чата для уведомлений'


class CustomSetPasswordForm(StyleFormMixin, SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = ('Новый пароль')
        self.fields['new_password2'].label = ('Подтверждение пароля')

        self.fields['new_password1'].help_text = None
        self.fields['new_password1'].widget.attrs.pop('aria-describedby', None)
        self.fields['new_password1'].widget.attrs.pop('data-toggle', None)
        self.fields['new_password1'].widget.attrs.pop('data-placement', None)

        self.fields['new_password1'].help_text = (
            '<ul>'
            '<li>Ваш пароль не должен быть слишком похож на другую вашу личную информацию.</li>'
            '<li>Ваш пароль должен содержать не менее 8 символов.</li>'
            '<li>Ваш пароль не должен быть слишком простым.</li>'
            '<li>Ваш пароль не может состоять только из цифр.</li>'
            '</ul>'
        )
