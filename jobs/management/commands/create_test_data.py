from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import EmployerProfile, JobSeekerProfile, Notification
from applications.models import Application, Resume
from jobs.models import Job

User = get_user_model()


class Command(BaseCommand):
    help = "Create demo/test data (users, jobs, resumes, applications). Safe to run multiple times."

    def handle(self, *args, **options):

        employer, _ = User.objects.get_or_create(
            username="employer1",
            defaults={"email": "employer1@example.com"},
        )
        employer.is_employer = True
        employer.is_active = True
        employer.is_verified = True
        employer.set_password("employerpass")
        employer.save()

        EmployerProfile.objects.update_or_create(
            user=employer,
            defaults={
                "company_name": "Acme Co",
                "company_description": "A demo company for showcasing the project.",
            },
        )

        seeker1, _ = User.objects.get_or_create(
            username="seeker1",
            defaults={"email": "seeker1@example.com"},
        )
        seeker1.is_employer = False
        seeker1.is_active = True
        seeker1.is_verified = True
        seeker1.set_password("seekerpass")
        seeker1.save()

        JobSeekerProfile.objects.update_or_create(
            user=seeker1,
            defaults={
                "education": "BSc Computer Engineering",
                "skills": "Python, Django, REST, PostgreSQL, Git",
            },
        )

        seeker2, _ = User.objects.get_or_create(
            username="seeker2",
            defaults={"email": "seeker2@example.com"},
        )
        seeker2.is_employer = False
        seeker2.is_active = True
        seeker2.is_verified = True
        seeker2.set_password("seekerpass")
        seeker2.save()

        JobSeekerProfile.objects.update_or_create(
            user=seeker2,
            defaults={
                "education": "BSc Software Engineering",
                "skills": "React, TypeScript, HTML/CSS, REST",
            },
        )


        job1, created = Job.objects.get_or_create(
            employer=employer,
            title="Backend Django Developer",
            defaults={
                "description": "Build and maintain REST APIs, authentication, and background tasks.",
                "benefits": "Remote / Hybrid, Medical insurance, Flexible hours",
                "requirements": "Python, Django, REST, PostgreSQL, Git",
                "salary_min": 3000,
                "salary_max": 4500,
                "is_active": True,
            },
        )
        if not created:
            Job.objects.filter(pk=job1.pk).update(
                description="Build and maintain REST APIs, authentication, and background tasks.",
                benefits="Remote / Hybrid, Medical insurance, Flexible hours",
                requirements="Python, Django, REST, PostgreSQL, Git",
                salary_min=3000,
                salary_max=4500,
                is_active=True,
            )

        job2, created = Job.objects.get_or_create(
            employer=employer,
            title="Frontend React Developer",
            defaults={
                "description": "Work with React, build UI components, and integrate with APIs.",
                "benefits": "Remote, Learning budget, Team retreats",
                "requirements": "JavaScript/TypeScript, React, HTML/CSS",
                "salary_min": 2500,
                "salary_max": 4200,
                "is_active": True,
            },
        )
        if not created:
            Job.objects.filter(pk=job2.pk).update(
                description="Work with React, build UI components, and integrate with APIs.",
                benefits="Remote, Learning budget, Team retreats",
                requirements="JavaScript/TypeScript, React, HTML/CSS",
                salary_min=2500,
                salary_max=4200,
                is_active=True,
            )


        def ensure_resume(user, filename, content: str) -> Resume:
            existing = Resume.objects.filter(applicant=user).first()
            if existing:
                return existing
            r = Resume(applicant=user)
            r.file.save(filename, ContentFile(content), save=True)
            return r

        r1 = ensure_resume(
            seeker1,
            "seeker1_resume.txt",
            "Name: Seeker1\nSkills: Python, Django, REST, PostgreSQL\nProjects: Job board (Django)\n",
        )
        r2 = ensure_resume(
            seeker2,
            "seeker2_resume.txt",
            "Name: Seeker2\nSkills: React, TypeScript, HTML/CSS\nProjects: UI dashboards\n",
        )


        app1, created = Application.objects.get_or_create(
            job=job1,
            applicant=seeker1,
            defaults={
                "resume": r1,
                "cover_letter": "I’m excited to apply. I’ve built Django projects with Postgres and REST APIs.",
                "status": "pending",
            },
        )
        if not created:
            if app1.resume_id is None:
                app1.resume = r1
            app1.cover_letter = app1.cover_letter or "I’m excited to apply. I’ve built Django projects with Postgres and REST APIs."
            app1.status = app1.status or "pending"
            app1.save()

        app2, created = Application.objects.get_or_create(
            job=job2,
            applicant=seeker2,
            defaults={
                "resume": r2,
                "cover_letter": "I have strong React/TS skills and I’m comfortable with API integration.",
                "status": "accepted",
                "interview_date": timezone.now() + timedelta(days=3),
            },
        )
        if not created:
            if app2.resume_id is None:
                app2.resume = r2
            app2.cover_letter = app2.cover_letter or "I have strong React/TS skills and I’m comfortable with API integration."
            if app2.status == "pending":
                app2.status = "accepted"
            if app2.interview_date is None and app2.status == "accepted":
                app2.interview_date = timezone.now() + timedelta(days=3)
            app2.save()

        def ensure_notification(user, title, message):
            if not Notification.objects.filter(user=user, title=title, message=message).exists():
                Notification.objects.create(user=user, title=title, message=message)

        ensure_notification(
            seeker1,
            "Application Submitted",
            f"You applied to '{job1.title}'. Status: Pending.",
        )
        ensure_notification(
            seeker2,
            "Application Accepted",
            f"Your application for '{job2.title}' was accepted."
            + (f" Interview: {app2.interview_date}" if app2.interview_date else ""),
        )

        self.stdout.write(self.style.SUCCESS("Demo data created/updated successfully."))
        self.stdout.write("Login credentials (demo):")
        self.stdout.write("  Employer -> username: employer1  password: employerpass")
        self.stdout.write("  Seeker1  -> username: seeker1   password: seekerpass")
        self.stdout.write("  Seeker2  -> username: seeker2   password: seekerpass")
