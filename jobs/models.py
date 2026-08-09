from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse


class JobQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def search(self, q):
        if not q:
            return self
        q = q.strip()
        return self.filter(
            Q(title__icontains=q) |
            Q(benefits__icontains=q) |
            Q(requirements__icontains=q) |
            Q(description__icontains=q)
        )

    def filter_advanced(self, title=None, benefits=None, salary_min=None, salary_max=None):
        qs = self
        if title:
            qs = qs.filter(title__icontains=title.strip())
        if benefits:
            qs = qs.filter(benefits__icontains=benefits.strip())
        if salary_min is not None:
            qs = qs.filter(salary_max__gte=salary_min)
        if salary_max is not None:
            qs = qs.filter(salary_min__lte=salary_max)

        return qs

    def recommend_for_user(self, user, limit=5):
        qs = self.active()

        if not getattr(user, "is_authenticated", False) or getattr(user, "is_employer", False):
            return qs.order_by("-id")[:limit]

        try:
            from applications.models import Application

            applied_job_ids = Application.objects.filter(applicant=user).values_list("job_id", flat=True)

            recent_jobs = qs.filter(id__in=applied_job_ids).order_by("-id")[:10]

            keywords = []
            for j in recent_jobs:
                if j.title:
                    keywords += j.title.split()
                if getattr(j, "benefits", None):
                    keywords += str(j.benefits).split()

            keywords = [k.strip() for k in keywords if len(k.strip()) >= 3][:8]

            if keywords:
                q_obj = Q()
                for k in keywords:
                    q_obj |= Q(title__icontains=k) | Q(benefits__icontains=k)

                return qs.exclude(id__in=applied_job_ids).filter(q_obj).order_by("-id")[:limit]

            return qs.exclude(id__in=applied_job_ids).order_by("-id")[:limit]

        except Exception:
            return qs.order_by("-id")[:limit]


class JobManager(models.Manager):
    def get_queryset(self):
        return JobQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def search(self, q):
        return self.get_queryset().search(q)

    def filter_advanced(self, **kwargs):
        return self.get_queryset().filter_advanced(**kwargs)

    def recommend_for_user(self, user, limit=5):
        return self.get_queryset().recommend_for_user(user=user, limit=limit)


class Job(models.Model):
    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jobs"
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = JobManager()

    class Meta:
        ordering = ["-created_at"]

    def get_absolute_url(self):
        return reverse("jobs:job-detail", args=[self.pk])

    def __str__(self):
        return self.title
