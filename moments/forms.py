from django import forms
from moments.models import Moment
from django import forms
from moments.models import Moment

# class StyleFormMixin:
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             if isinstance(field, BooleanField):
#                 if 'class' not in field.widget.attrs:
#                     field.widget.attrs['class'] = 'form-check-input'
#             else:
#                 if 'class' not in field.widget.attrs:
#                     field.widget.attrs['class'] = 'form-control'


class MomentForm(forms.ModelForm):
    class Meta:
        model = Moment
        fields = ["title", "comments", "photo", "video", "location", "is_public"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Введите заголовок"}
            ),
            "comments": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Введите комментарий",
                }
            ),
            "photo": forms.FileInput(attrs={"class": "form-control"}),
            "video": forms.FileInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Укажите место"}
            ),
            "is_public": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, "fields") and isinstance(self.fields, dict):
            for field_name, field in self.fields.items():
                if isinstance(field, forms.BooleanField):
                    if "class" not in field.widget.attrs:
                        field.widget.attrs["class"] = "form-check-input"
                else:
                    if "class" not in field.widget.attrs:
                        field.widget.attrs["class"] = "form-control"
