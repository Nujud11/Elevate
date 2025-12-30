# companies/views.py
from django.db import models
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.views import View
from django.http import HttpResponse
import csv

from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from accounts.mixins import RoleRequiredMixin
from internships.models import Internship
from applications.models import Application
from applications.forms import ApplicationStatusForm   
from .forms import InternshipForm



@method_decorator(never_cache, name='dispatch')
class CompanyPostingsView(RoleRequiredMixin, LoginRequiredMixin, ListView):
    required_role = "company"
    template_name = "companies/postings.html" 
    context_object_name = "internships"
    model = Internship
    paginate_by = 6 
    def get_queryset(self):
        qs = Internship.objects.filter(owner=self.request.user).order_by("-posted_at")
        self.total_count = qs.count() 
        qs = qs.annotate(applicant_count=Count('applications')) 
        q = self.request.GET.get("q", "")
        remote_filter = self.request.GET.get("remote_filter", "")
        if q: qs = qs.filter(title__icontains=q)
        if remote_filter == "1": qs = qs.filter(is_remote=True)
        elif remote_filter == "0": qs = qs.filter(is_remote=False)
        return qs
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_count"] = self.total_count 
        ctx["q"] = self.request.GET.get("q", "")
        ctx["remote_filter"] = self.request.GET.get("remote_filter", "")
        return ctx

@method_decorator(never_cache, name='dispatch')
class InternshipCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    required_role = "company"
    model = Internship
    form_class = InternshipForm
    template_name = "companies/form.html"
    success_url = reverse_lazy("company_postings")
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        messages.success(self.request, "Internship created.")
        return super().form_valid(form)


@method_decorator(never_cache, name='dispatch')
class InternshipUpdateView(RoleRequiredMixin, LoginRequiredMixin, UpdateView):
    required_role = "company"
    model = Internship
    form_class = InternshipForm
    template_name = "companies/form.html"
    success_url = reverse_lazy("company_postings")
    def get_queryset(self):
        return Internship.objects.filter(owner=self.request.user)
    def form_valid(self, form):
        messages.success(self.request, "Internship updated.")
        return super().form_valid(form)

class ApplicationFilterMixin:
    """
    A shared Mixin to provide search and filter logic
    for both application list views.
    """
    def get_filtered_queryset(self, base_qs):
        """
        Applies search and status filters to a base queryset.
        """
        q = self.request.GET.get("q", "").strip()
        status_value = self.request.GET.get("status", "")

        if q:
            base_qs = base_qs.filter(
                Q(student__username__icontains=q) |
                Q(student__email__icontains=q) |
                Q(student__profile__full_name__icontains=q)
            )

        status_choices_dict = dict(Application._meta.get_field("status").choices)
        if status_value in status_choices_dict:
            base_qs = base_qs.filter(status=status_value)
        
        return base_qs

    def get_context_data(self, **kwargs):
        """
        Passes the filter values and choices back to the template.
        """
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["status"] = self.request.GET.get("status", "")
        status_choices = [("", "All")] + Application._meta.get_field("status").choices
        ctx["status_choices"] = status_choices
        return ctx
    
@method_decorator(never_cache, name='dispatch')
class CompanyAllApplicationsView(ApplicationFilterMixin, RoleRequiredMixin, LoginRequiredMixin, ListView):
    required_role = "company"
    template_name = "companies/all_applications.html"
    context_object_name = "applications"
    model = Application
    paginate_by = 20
    def get_queryset(self):
        base_qs = (
            Application.objects
            .filter(internship__owner=self.request.user)
            .select_related("student", "internship", "student__profile")
            .order_by("-submitted_at")
        )
        return self.get_filtered_queryset(base_qs)
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

@method_decorator(never_cache, name='dispatch')
class CompanyApplicationsView(ApplicationFilterMixin, RoleRequiredMixin, LoginRequiredMixin, ListView):
    required_role = "company"
    template_name = "companies/applications.html"
    context_object_name = "applications"
    model = Application
    paginate_by = 20
    def get_queryset(self):
        pk = self.kwargs["pk"]
        self.base_queryset = (
            Application.objects
            .filter(internship__pk=pk, internship__owner=self.request.user)
            .select_related("student", "internship", "student__profile")
        )
        qs = self.base_queryset.order_by("-submitted_at")
        return self.get_filtered_queryset(qs)
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_applicants_count"] = self.base_queryset.count()
        ctx["posting_id"] = self.kwargs["pk"]
        ctx["internship"] = get_object_or_404(Internship, pk=self.kwargs["pk"], owner=self.request.user)
        return ctx

@method_decorator(never_cache, name='dispatch')
class ApplicationStatusUpdateView(RoleRequiredMixin, LoginRequiredMixin, View):
    """
    Handles the POST request from the status dropdown on the applications list.
    """
    required_role = "company"

    def post(self, request, pk):
        app = get_object_or_404(
            Application,
            pk=pk,
            internship__owner=request.user
        )

        form = ApplicationStatusForm(request.POST, instance=app)
        if form.is_valid():
            form.save()
            messages.success(request, "Application status updated.")
        else:
            err = form.errors.get("status")
            messages.error(request, f"Invalid status value. {err[0] if err else ''}")

        # --- THIS IS THE FIX ---
        # Check where the user came from and redirect them back
        referer_url = request.META.get('HTTP_REFERER', '')
        
        # 'app' is the application object we just saved
        if f'internships/{app.internship.pk}/applications' in referer_url:
            # If they were on the specific internship page, redirect back there
            return redirect("company_applications", pk=app.internship.pk)
        
        # Otherwise, send them to the default "all applications" page
        return redirect("company_all_applications")

@method_decorator(never_cache, name='dispatch')
class CompanyApplicationsCSVView(ApplicationFilterMixin, RoleRequiredMixin, LoginRequiredMixin, ListView):
    required_role = "company"
    model = Application

    def get(self, request, *args, **kwargs):
        # 1. Get the base queryset
        pk = self.kwargs.get("pk") # Use .get() to be safe
        
        if pk:
            # This is for a specific internship
            base_qs = (
                Application.objects
                .filter(internship__pk=pk, internship__owner=self.request.user)
                .select_related("student", "internship")
            )
        else:
            # This is for ALL internships
            base_qs = (
                Application.objects
                .filter(internship__owner=self.request.user)
                .select_related("student", "internship")
            )
        
        # 2. Apply filters from the mixin
        apps = self.get_filtered_queryset(base_qs)

        # 3. Create the CSV
        filename = f'applications_{pk}.csv' if pk else 'all_applications.csv'
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(resp)
        writer.writerow(["Internship", "Student", "Email", "Status", "Submitted At", "CV URL"])
        for a in apps:
            writer.writerow([
                a.internship.title,
                a.student.username,
                getattr(a.student, "email", ""),
                a.get_status_display(),
                a.submitted_at.isoformat(),
                (request.build_absolute_uri(a.cv.url) if a.cv else ""),
            ])
        return resp