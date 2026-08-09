from django.contrib import admin
from .models import Resume, Application

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('applicant','file','uploaded_at')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job','applicant','status','applied_at')
    list_filter = ('status',)

