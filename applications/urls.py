from django.urls import path
from . import views

app_name = "applications"

urlpatterns = [
    path("resume/upload/", views.upload_resume, name="upload-resume"),
    path("resumes/", views.resume_list, name="resume-list"),
    path("job/<int:job_pk>/apply/", views.apply_to_job, name="apply"),
    path("job/<int:job_pk>/applicants/", views.applicants_list, name="applicants-list"),
    path("application/<int:app_pk>/update/", views.update_application_status, name="update-application"),
    path("resume/<int:resume_pk>/download/", views.download_resume, name="download-resume"),
    path("my-applications/", views.my_applications, name="my_applications"),
]
