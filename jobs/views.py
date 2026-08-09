from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from .models import Job
from .forms import JobForm

import logging
logger = logging.getLogger("jobs")


class JobListView(ListView):
    model = Job
    template_name = "jobs/job_list.html"
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get("q")
        title = self.request.GET.get("title")
        benefits = self.request.GET.get("benefits")

        smin = self.request.GET.get("salary_min")
        smax = self.request.GET.get("salary_max")

        def to_int(x):
            try:
                return int(x) if x not in (None, "", "None") else None
            except (ValueError, TypeError):
                return None

        salary_min = to_int(smin)
        salary_max = to_int(smax)

        qs = Job.objects.active().search(q).filter_advanced(
            title=title,
            benefits=benefits,
            salary_min=salary_min,
            salary_max=salary_max,
        )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["can_create_job"] = self.request.user.is_authenticated and getattr(self.request.user, "is_employer", False)
        ctx["recommended_jobs"] = Job.objects.recommend_for_user(self.request.user, limit=5)
        return ctx


class JobDetailView(DetailView):
    model = Job
    template_name = "jobs/job_detail.html"


class EmployerRequiredMixin(UserPassesTestMixin):
    raise_exception = False

    def test_func(self):
        return self.request.user.is_authenticated and getattr(self.request.user, "is_employer", False)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.info(self.request, "Please log in first.")
            return redirect(f"{reverse('accounts:login')}?next={self.request.path}")
        messages.error(self.request, "Only employers can access this page.")
        return redirect("jobs:job-list")


class JobCreateView(LoginRequiredMixin, EmployerRequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = "jobs/job_form.html"

    def form_valid(self, form):
        form.instance.employer = self.request.user
        resp = super().form_valid(form)
        logger.info(f"Job created | id={self.object.id} | title={self.object.title} | employer={self.request.user.username}")
        messages.success(self.request, "Job created successfully.")
        return resp


class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = "jobs/job_form.html"

    def test_func(self):
        job = self.get_object()
        return job.employer == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, "You are not allowed to edit this job.")
        return redirect("jobs:job-list")

    def form_valid(self, form):
        resp = super().form_valid(form)
        logger.info(f"Job updated | id={self.object.id} | title={self.object.title} | employer={self.request.user.username}")
        messages.success(self.request, "Job updated successfully.")
        return resp


class JobDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Job
    template_name = "jobs/job_confirm_delete.html"
    success_url = reverse_lazy("jobs:job-list")

    def test_func(self):
        return self.get_object().employer == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, "You are not allowed to delete this job.")
        return redirect("jobs:job-list")

    def delete(self, request, *args, **kwargs):
        job = self.get_object()
        resp = super().delete(request, *args, **kwargs)
        logger.info(f"Job deleted | id={job.id} | title={job.title} | employer={request.user.username}")
        messages.info(request, "Job deleted.")
        return resp


from django.contrib.auth.decorators import login_required

@login_required
def employer_dashboard(request):
    if not getattr(request.user, "is_employer", False):
        messages.error(request, "Only employers can view the employer dashboard.")
        return redirect("jobs:job-list")

    jobs = request.user.jobs.all()
    return render(request, "jobs/employer_dashboard.html", {"jobs": jobs})
