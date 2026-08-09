import os
from django.db import models
from django.conf import settings
from jobs.models import Job


class ResumeQuerySet(models.QuerySet):

    def for_user(self, user):
        return self.filter(applicant=user)


class ResumeManager(models.Manager):

    def get_queryset(self):
        return ResumeQuerySet(self.model, using=self._db)


    def for_user(self, user):
        return self.get_queryset().for_user(user)


class ApplicationQuerySet(models.QuerySet):

    def pending(self):
        return self.filter(status='pending')


    def for_employer(self, employer_user):
        return self.filter(job__employer=employer_user)


    def for_applicant(self, applicant_user):
        return self.filter(applicant=applicant_user)


class ApplicationManager(models.Manager):
    def get_queryset(self):
        return ApplicationQuerySet(self.model, using=self._db)

    def pending(self):
        return self.get_queryset().pending()

    def for_employer(self, employer_user):
        return self.get_queryset().for_employer(employer_user)

    def for_applicant(self, applicant_user):
        return self.get_queryset().for_applicant(applicant_user)


class PendingApplicationManager(ApplicationManager):
    def get_queryset(self):
        return super().get_queryset().pending()

def resume_upload_to(instance, filename):
    username = getattr(instance, 'applicant', None)
    username = username.username if username else 'anonymous'
    filename = os.path.basename(filename)
    return f"resumes/{username}/{filename}"

class Resume(models.Model):
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes'
    )
    file = models.FileField(upload_to=resume_upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    objects = ResumeManager()

    def __str__(self):
        return f"{self.applicant.username} - {self.file.name}"

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        null=True,
        blank=True,
    )
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True)
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    interview_date = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    objects = ApplicationManager()
    pending_apps = PendingApplicationManager()

    class Meta:
        unique_together = ('job', 'applicant')

    def __str__(self):
        return f"{self.applicant.username if self.applicant else 'Unknown'} -> {self.job.title} ({self.status})"

