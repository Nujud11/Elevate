# students/views.py
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from accounts.mixins import RoleRequiredMixin
from internships.models import Internship
from applications.models import Application
from applications.forms import ApplicationCreateForm

# 1) OPEN PAGES (no login required)

@method_decorator(never_cache, name='dispatch')
class StudentBrowseView(ListView):
    template_name = "students/browse.html"
    context_object_name = "internships"
    paginate_by = 6
    model = Internship

    def get_queryset(self):
        qs = Internship.objects.filter(is_active=True).order_by("-posted_at")
        qs = qs.annotate(applicant_count=Count('applications')) 
        self.total_count = qs.count() 
        
        q = self.request.GET.get("q", "")
        loc = self.request.GET.get("loc", "")
        comp = self.request.GET.get("comp", "")
        remote_filter = self.request.GET.get("remote_filter", "")

        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q)
            )
        if loc:
            qs = qs.filter(location__icontains=loc) 
        if comp:
            qs = qs.filter(owner__username__icontains=comp) 
        if remote_filter == "1":
            qs = qs.filter(is_remote=True)
        elif remote_filter == "0":
            qs = qs.filter(is_remote=False)
            
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_count"] = self.total_count
        ctx["q"] = self.request.GET.get("q", "")
        ctx["loc"] = self.request.GET.get("loc", "")
        ctx["comp"] = self.request.GET.get("comp", "")
        ctx["remote_filter"] = self.request.GET.get("remote_filter", "")
        
        active_internships = Internship.objects.filter(is_active=True)
        
        ctx["all_titles"] = active_internships.values_list(
            'title', flat=True
        ).distinct().order_by('title')
        
        ctx["all_locations"] = active_internships.exclude(
            location__exact=''
        ).values_list('location', flat=True).distinct().order_by('location')
        
        ctx["all_companies"] = active_internships.values_list(
            'owner__username', flat=True
        ).distinct().order_by('owner__username')
        
        # Get a list of internship IDs that the logged-in student has applied to.
        applied_internship_ids = []
        if self.request.user.is_authenticated and self.request.user.profile.is_student:
            applied_internship_ids = Application.objects.filter(
                student=self.request.user
            ).values_list('internship_id', flat=True)
        
        ctx['applied_internship_ids'] = set(applied_internship_ids)
        
        return ctx
    
    def get_template_names(self):
        """
        This is the "brain" for HTMX.
        It checks if the request is from HTMX by looking for the 'HX-Request' header.
        """
        
        if self.request.headers.get('HX-Request') == 'true':
            # If it's an HTMX request, render *only* the partial.
            return ["students/partials/_internship_list.html"]
        
        # Otherwise, render the full page.
        return [self.template_name]


@method_decorator(never_cache, name='dispatch')
class StudentDetailView(DetailView):
    template_name = "students/detail.html"
    context_object_name = "job"
    model = Internship

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        already = False
        submitted_at = None
        if self.request.user.is_authenticated:
            # We get the profile here to be safe
            if hasattr(self.request.user, 'profile') and self.request.user.profile.is_student:
                application = Application.objects.filter(
                    internship=self.object, student=self.request.user
                ).first()
                if application:
                    already = True
                    submitted_at = application.submitted_at
        ctx["already_applied"] = already
        ctx["submitted_at"] = submitted_at 
        return ctx

# 2) LOGIN-ONLY PAGES
@method_decorator(never_cache, name='dispatch')
class StudentApplyView(LoginRequiredMixin, FormView):
    template_name = "students/apply.html"
    form_class = ApplicationCreateForm

    def dispatch(self, request, *args, **kwargs):
        self.job = get_object_or_404(Internship, pk=kwargs["pk"], is_active=True)
        
        if request.user.is_authenticated and Application.objects.filter(
            internship=self.job, student=request.user
        ).exists():
            messages.info(request, "You’ve already applied to this internship.")
            return redirect("student_detail", pk=self.job.pk)
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["job"] = self.job
        return ctx
    
    def form_valid(self, form):
        """
        This is the correct, simple, one-stage save.
        """
        # 1. Check for race conditions
        exists = Application.objects.filter(
            internship=self.job, student=self.request.user
        ).exists()
        if exists:
            messages.info(self.request, "You’ve already applied to this internship.")
            return redirect("student_detail", pk=self.job.pk)

        # 2. Get the object from the form, but don't save to DB yet.
        application = form.save(commit=False)
        
        # 3. Add the related objects (the internship and student)
        application.internship = self.job
        application.student = self.request.user
        
        # 4. NOW save everything *once*.
        # This will create the DB object and save the files to S3.
        application.save() 
        
        messages.success(self.request, "Application submitted successfully.")
        
        # 5. Redirect
        return redirect("student_apps")


@method_decorator(never_cache, name='dispatch')
class StudentApplicationsView(LoginRequiredMixin, ListView):
    template_name = "students/my_applications.html"
    context_object_name = "applications"

    def get_queryset(self):
        return (
            Application.objects
            .filter(student=self.request.user)
            .select_related("internship")
            .order_by("-submitted_at")
        )