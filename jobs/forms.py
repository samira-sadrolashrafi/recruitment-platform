from django import forms
from .models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title",
            "description",
            "salary_min",
            "salary_max",
            "benefits",
            "requirements",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "benefits": forms.Textarea(attrs={"rows": 3}),
            "requirements": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        mn = cleaned.get("salary_min")
        mx = cleaned.get("salary_max")
        if mn and mx and mn > mx:
            self.add_error("salary_max", "salary_max must be >= salary_min")
        return cleaned
