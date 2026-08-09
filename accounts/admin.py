from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, EmployerProfile, JobSeekerProfile, Notification

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        ("Role & Extra", {"fields": ("is_employer", "phone_number", "is_verified")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role & Extra", {"fields": ("is_employer", "phone_number", "is_verified")}),
    )

    list_display = ("username", "email", "phone_number", "is_employer", "is_active", "is_staff", "is_superuser")
    list_filter = ("is_employer", "is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "phone_number")
    ordering = ("username",)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.is_staff = obj.is_staff or obj.is_superuser
        super().save_model(request, obj, form, change)

@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name")
    search_fields = ("user__username", "company_name")

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "education")
    search_fields = ("user__username", "education")

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "title")
