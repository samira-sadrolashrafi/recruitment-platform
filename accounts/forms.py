from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        label="Phone Number",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    is_employer = forms.BooleanField(
        required=False,
        label="Register as Employer",
        widget=forms.CheckboxInput(attrs={"id": "id_is_employer", "class": "form-check-input"})
    )

    class Meta:
        model = User
        fields = ["username", "email", "phone_number", "password1", "password2", "is_employer"]


    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email is already registered.")
        return email


    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number", "").strip()
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        if phone.startswith("0"):
            phone = "+98" + phone[1:]

        qs = User.objects.filter(phone_number=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone


    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if password1:
            try:
                validate_password(password1, self.instance)
            except ValidationError as e:
                raise forms.ValidationError(e.messages)
        return password1


    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.phone_number = self.cleaned_data["phone_number"]
        user.is_employer = self.cleaned_data.get("is_employer", False)
        if commit:
            user.save()
        return user
