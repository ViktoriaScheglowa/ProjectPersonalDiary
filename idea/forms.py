from django import forms

from idea.models import Myidea


class IdeaForm(forms.ModelForm):
    class Meta:
        model = Myidea
        fields = ['title', 'comments', 'pictures', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок мысли'
            }),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Опишите вашу мысль...',
                'rows': 4
            }),
            'pictures': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'title': 'Заголовок',
            'comments': 'Комментарии',
            'pictures': 'Фото',
            'is_public': 'Сделать публичной'
        }
        help_texts = {
            'is_public': 'Отметьте, если хотите поделиться мыслью с другими пользователями'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'fields') and isinstance(self.fields, dict):
            for field_name, field in self.fields.items():
                if isinstance(field, forms.BooleanField):
                    if 'class' not in field.widget.attrs:
                        field.widget.attrs['class'] = 'form-check-input'
                else:
                    if 'class' not in field.widget.attrs:
                        field.widget.attrs['class'] = 'form-control'
