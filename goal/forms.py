from django import forms

from goal.models import Goal


class GoalForms(forms.ModelForm):
    class Meta:
        model = Goal
        fields = [
            "title",
            "comments",
            "photo",
            "video",
            "location",
            "is_public",
            "date_deadline",
            "time_deadline",
        ]
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
            "date_deadline": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "time_deadline": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
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
