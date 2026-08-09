from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import random


class CustomUser(AbstractUser):
    is_employer = models.BooleanField(default=False, verbose_name="Is Employer")
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False)  # تایید OTP پیامک و ایمیل

    def __str__(self):
        return self.username



class EmployerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="employer_profile")
    company_name = models.CharField(max_length=200, blank=True)
    company_description = models.TextField(blank=True)

    def __str__(self):
        return f"Employer: {self.user.username}"


class JobSeekerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="jobseeker_profile")
    education = models.CharField(max_length=200, blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated skills, e.g. Python, Django, SQL")

    def __str__(self):
        return f"JobSeeker: {self.user.username}"



class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=120)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"



@receiver(post_save, sender=CustomUser)
def create_or_update_user_profiles(sender, instance, created, **kwargs):
    if instance.is_employer:
        EmployerProfile.objects.get_or_create(user=instance)
        JobSeekerProfile.objects.filter(user=instance).delete()
    else:
        JobSeekerProfile.objects.get_or_create(user=instance)
        EmployerProfile.objects.filter(user=instance).delete()



class PhoneOTP(models.Model):
    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=2)

    @staticmethod
    def generate():
        return str(random.randint(100000, 999999))



class EmailOTP(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    @staticmethod
    def generate():
        return str(random.randint(100000, 999999))
