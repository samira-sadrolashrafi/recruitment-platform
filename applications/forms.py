from django import forms

from .models import Resume, Application


class ResumeUploadForm(forms.ModelForm):

    class Meta:
        model = Resume
        fields = ["file"]

    def clean_file(self):
        f = self.cleaned_data.get("file")

        if f:
            if f.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "Resume file too large (max 5MB)."
                )

            if not f.name.lower().endswith(
                (".pdf", ".doc", ".docx", ".txt")
            ):
                raise forms.ValidationError(
                    "Allowed file types: pdf, doc, docx, txt"
                )

        return f


class ApplicationForm(forms.ModelForm):

    class Meta:
        model = Application
        fields = ["cover_letter", "resume"]
        widgets = {
            "cover_letter": forms.Textarea(
                attrs={"rows": 4}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # By default, no resumes are available.
        self.fields["resume"].queryset = Resume.objects.none()

        # Only allow the logged-in user to select their own resumes.
        if user is not None and user.is_authenticated:
            self.fields["resume"].queryset = (
                Resume.objects
                .for_user(user)
                .order_by("-uploaded_at")
            )

        # Apply Bootstrap styling to form fields.
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})