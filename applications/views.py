import os
import logging
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ResumeUploadForm, ApplicationForm
from .models import Resume, Application
from jobs.models import Job
from accounts.models import Notification

logger = logging.getLogger("applications")


@login_required
def upload_resume(request):
    if request.method == "POST":
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            r = form.save(commit=False)
            r.applicant = request.user
            r.save()
            messages.success(request, "Resume uploaded.")
            logger.info(f"Resume uploaded | resume_id={r.id} | user={request.user.username} | file={r.file.name}")
            return redirect("applications:resume-list")
    else:
        form = ResumeUploadForm()
        for f in form.fields:
            form.fields[f].widget.attrs.update({"class": "form-control"})

    return render(request, "applications/upload_resume.html", {"form": form})


@login_required
def resume_list(request):
    resumes = Resume.objects.for_user(request.user).order_by("-uploaded_at")
    return render(request, "applications/resume_list.html", {"resumes": resumes})


@login_required
def apply_to_job(request, job_pk):
    job = get_object_or_404(Job, pk=job_pk)

    if getattr(request.user, "is_employer", False):
        messages.error(request, "Employers cannot apply for jobs.")
        return redirect(job.get_absolute_url())

    error_message = None

    if request.method == "POST":
        form = ApplicationForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():
            existing = Application.objects.filter(
                job=job,
                applicant=request.user,
            ).first()

            if existing:
                error_message = "You have already applied to this job."

            else:
                app = form.save(commit=False)
                app.job = job
                app.applicant = request.user
                app.save()

                Notification.objects.create(
                    user=request.user,
                    title="Application Submitted",
                    message=(
                        f"You applied to '{job.title}'. "
                        "Status: Pending."
                    ),
                )

                messages.success(
                    request,
                    "Application submitted.",
                )

                logger.info(
                    f"Job application submitted | "
                    f"application_id={app.id} | "
                    f"job_id={job.id} | "
                    f"applicant={request.user.username}"
                )

                return redirect(
                    "jobs:job-detail",
                    pk=job.pk,
                )

    else:
        form = ApplicationForm(
            user=request.user,
        )

    return render(
        request,
        "applications/apply.html",
        {
            "form": form,
            "job": job,
            "error_message": error_message,
        },
    )


@login_required
def applicants_list(request, job_pk):
    job = get_object_or_404(Job, pk=job_pk)
    if job.employer != request.user:
        raise Http404

    apps = (
        Application.objects.for_employer(request.user)
        .filter(job=job)
        .select_related("applicant", "resume")
    )
    return render(request, "applications/applicants_list.html", {"applications": apps, "job": job})


@login_required
def update_application_status(request, app_pk):
    app = get_object_or_404(Application, pk=app_pk)
    if app.job.employer != request.user:
        raise Http404

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "accept":
            app.status = "accepted"
            date_str = request.POST.get("interview_date")
            app.interview_date = date_str or None
            app.save()

            if app.applicant and app.applicant.email:
                send_mail(
                    "Application Accepted",
                    f"Hi {app.applicant.username},\n\nYour application for '{app.job.title}' was accepted."
                    + (f"\nInterview: {app.interview_date}\n" if app.interview_date else "\n")
                    + "\nThanks!",
                    getattr(settings, "DEFAULT_FROM_EMAIL", None),
                    [app.applicant.email],
                    fail_silently=True,
                )

            if app.applicant:
                Notification.objects.create(
                    user=app.applicant,
                    title="Application Accepted",
                    message=f"Your application for '{app.job.title}' was accepted."
                    + (f" Interview: {app.interview_date}" if app.interview_date else ""),
                )

            messages.success(request, "Applicant accepted.")
            logger.info(f"Application accepted | application_id={app.id} | job_id={app.job.id} | applicant={app.applicant.username} | employer={request.user.username}")

        elif action == "reject":
            app.status = "rejected"
            app.save()

            if app.applicant and app.applicant.email:
                send_mail(
                    "Application Rejected",
                    f"Hi {app.applicant.username},\n\nYour application for '{app.job.title}' was rejected.\n\nThanks!",
                    getattr(settings, "DEFAULT_FROM_EMAIL", None),
                    [app.applicant.email],
                    fail_silently=True,
                )

            if app.applicant:
                Notification.objects.create(
                    user=app.applicant,
                    title="Application Rejected",
                    message=f"Your application for '{app.job.title}' was rejected.",
                )

            messages.info(request, "Applicant rejected.")
            logger.info(f"Application rejected | application_id={app.id} | job_id={app.job.id} | applicant={app.applicant.username} | employer={request.user.username}")

        return redirect("applications:applicants-list", job_pk=app.job.pk)

    return render(request, "applications/update_status.html", {"application": app})


@login_required
def download_resume(request, resume_pk):
    resume = get_object_or_404(Resume, pk=resume_pk)

    # allowed: owner or employer who has an application with that resume
    if resume.applicant != request.user:
        allowed = resume.application_set.filter(job__employer=request.user).exists()
        if not allowed:
            raise Http404

    try:
        path = resume.file.path
    except Exception:
        messages.error(request, "Resume file is not available.")
        raise Http404

    if os.path.exists(path):
        with open(path, "rb") as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response["Content-Disposition"] = f'attachment; filename={os.path.basename(path)}'
            return response

    messages.error(request, "Resume file not found on server.")
    raise Http404


@login_required
def my_applications(request):
    apps = Application.objects.for_applicant(request.user).select_related("job", "resume")
    logger.info(f"My applications viewed | user={request.user.username} | total_applications={apps.count()}")
    return render(request, "applications/my_applications.html", {"applications": apps})
