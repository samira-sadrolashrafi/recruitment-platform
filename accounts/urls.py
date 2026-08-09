from django.urls import path
from . import views


app_name = "accounts"


urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("verify/", views.verify_otp_view, name="verify_otp"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_redirect, name="dashboard"),
    path("notifications/", views.notifications_list, name="notifications"),
    path("notifications/<int:pk>/read/", views.mark_notification_read, name="notification-read"),
]
