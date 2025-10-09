from django.forms import BooleanField
from django import forms
from moments.models import Moment


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if hasattr(field, 'widget') and hasattr(field.widget, 'attrs'):
                if 'class' not in field.widget.attrs:
                    if field.widget.__class__.__name__ in ['CheckboxInput', 'RadioSelect']:
                        field.widget.attrs['class'] = 'form-check-input'
                    else:
                        field.widget.attrs['class'] = 'form-control'


class MomentForm(forms.ModelForm):
    class Meta:
        model = Moment
        fields = ['title', 'comments', 'photo', 'video', 'location', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Введите комментарий'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Укажите место'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }