from django import forms

from habits.models import Habit


class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = [
            "action",
            "comments",
            "photo",
            "video",
            "location",
            "periodicity",
            "time_deadline",
            "time_to_complete",
            "is_public",
        ]
        widgets = {
            "action": forms.TextInput(
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
            "periodicity"
            "time_deadline"
            "time_to_complete"
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
