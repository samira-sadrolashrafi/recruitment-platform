import logging
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import UserRegisterForm
from .models import Notification, PhoneOTP, EmailOTP, CustomUser
from .utils import send_otp_sms, send_otp_email  # ارسال OTP (DEV mode)

logger = logging.getLogger("accounts")
User = get_user_model()



def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            phone = form.cleaned_data.get("phone_number")
            email = form.cleaned_data.get("email")

            if not user.is_superuser:
                sms_code = PhoneOTP.generate()
                PhoneOTP.objects.create(phone_number=phone, code=sms_code)
                send_otp_sms(phone, sms_code)

                email_code = EmailOTP.generate()
                EmailOTP.objects.create(email=email, code=email_code)
                send_otp_email(email, email_code)

                request.session["user_id_temp"] = user.id
                request.session["phone"] = phone
                request.session["email"] = email

                messages.success(request, "OTP sent to your phone and email.")

            logger.info(f"User registered | phone={phone} | email={email} | user_id={user.id} | superuser={user.is_superuser}")

            if not user.is_superuser:
                return redirect("accounts:verify_otp")
            else:
                return redirect("accounts:login")

    else:
        form = UserRegisterForm()

    return render(request, "accounts/register.html", {"form": form})



def verify_otp_view(request):
    user_id = request.session.get("user_id_temp")
    phone = request.session.get("phone")
    email = request.session.get("email")

    if not user_id or not phone or not email:
        messages.error(request, "No OTP verification in progress.")
        return redirect("accounts:register")

    dev_sms_otp = None
    dev_email_otp = None
    if settings.DEBUG:
        last_sms_otp = PhoneOTP.objects.filter(phone_number=phone).last()
        last_email_otp = EmailOTP.objects.filter(email=email).last()
        if last_sms_otp:
            dev_sms_otp = last_sms_otp.code
        if last_email_otp:
            dev_email_otp = last_email_otp.code

    if request.method == "POST":
        sms_code = request.POST.get("sms_otp")
        email_code = request.POST.get("email_otp")

        sms_entry = PhoneOTP.objects.filter(phone_number=phone, code=sms_code).last()
        email_entry = EmailOTP.objects.filter(email=email, code=email_code).last()

        if (
            sms_entry and not sms_entry.is_expired()
            and email_entry and not email_entry.is_expired()
        ):
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.is_verified = True
            user.save(update_fields=["is_active", "is_verified"])

            sms_entry.delete()
            email_entry.delete()
            request.session.pop("user_id_temp")
            request.session.pop("phone")
            request.session.pop("email")

            messages.success(request, "Your account has been verified!")
            logger.info(f"OTP verified | phone={phone} | email={email} | user_id={user.id}")

            return redirect("accounts:login")
        else:
            messages.error(request, "Invalid or expired OTPs.")

    return render(request, "accounts/verify.html", {
        "phone": phone,
        "email": email,
        "dev_sms_otp": dev_sms_otp,
        "dev_email_otp": dev_email_otp,
    })



def login_view(request):
    next_url = request.GET.get("next") or request.POST.get("next") or reverse("jobs:job-list")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            request.session["user_id"] = user.id
            request.session["username"] = user.username
            request.session["is_employer"] = user.is_employer

            if user.is_superuser:
                return redirect("/admin/")
            else:
                return redirect(next_url)
    else:
        form = AuthenticationForm(request)
        for f in form.fields:
            form.fields[f].widget.attrs.update({"class": "form-control"})

    return render(request, "accounts/login.html", {"form": form, "next": next_url})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("jobs:job-list")


@login_required
def dashboard_redirect(request):
    if request.user.is_superuser:
        return redirect("/admin/")
    if request.user.is_employer:
        return redirect("jobs:employer-dashboard")
    return redirect("applications:my_applications")



@login_required
def notifications_list(request):
    notes = request.user.notifications.all()
    unread_count = notes.filter(is_read=False).count()
    return render(request, "accounts/notifications.html", {
        "notifications": notes,
        "unread_count": unread_count
    })


@login_required
def mark_notification_read(request, pk):
    note = Notification.objects.filter(pk=pk, user=request.user).first()
    if note:
        note.is_read = True
        note.save(update_fields=["is_read"])
    return redirect("accounts:notifications")
