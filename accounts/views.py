
# accounts/views.py
from django.contrib.auth.mixins import LoginRequiredMixin # to restrict access to logged-in users
from django.urls import reverse_lazy,reverse
from django.views.generic import FormView, TemplateView, UpdateView 
from django.contrib.auth.views import LoginView 
from .forms import ( RegisterForm, StudentProfileForm, CompanyProfileForm, 
                    EducationFormSet, ExperienceFormSet)
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator


User = get_user_model()

from .models import Profile

class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"

    def form_valid(self, form):
        user = form.get_user() 
        
        selected_role = self.request.POST.get('role_type') 
        
        profile_role = getattr(user.profile, "role", None)

        if selected_role != profile_role:
            # If roles mismatch, add a form error and prevent login
            form.add_error(None, "Login failed: Your profile is registered as a '{}'.".format(profile_role))
            return self.form_invalid(form) # Return form invalid to stay on login page

        # If roles match, proceed with standard login process
        return super().form_valid(form)

    def get_success_url(self):
        # This determines the final redirect URL (as you noted, /c/ or /s/)
        role = getattr(self.request.user.profile, "role", None)
        if role == "student":
            return reverse('student_browse')  # Student goes to student browse page "/s/opportunities/" 
        elif role == "company":
            return reverse('company_postings') # Company goes to company management page  "/c/internships/"
        return "/" # Fallback


@method_decorator(never_cache, name='dispatch')
class ProfileDetailView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        pk = self.kwargs.get("pk")  # Get the user ID from the URL
        
        if pk:
            # Load the profile based on the ID in the URL (for public viewing)
            user_to_view = get_object_or_404(User, pk=pk)
            ctx["profile"] = user_to_view.profile
        else:
            # Load the profile of the currently logged-in user (for own viewing)
            ctx["profile"] = self.request.user.profile
            
        return ctx


@method_decorator(never_cache, name='dispatch')
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = "accounts/profile_form.html"
    success_url = reverse_lazy("account_profile")
    
    def get_form_class(self):
        if self.request.user.profile.is_student:
            return StudentProfileForm
        return CompanyProfileForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        """
        This function loads the formsets and sends them to the template.
        """
        ctx = super().get_context_data(**kwargs)
        
        # We only add formsets if the user is a Student
        if self.request.user.profile.is_student:
            if self.request.POST:
                # If form is being submitted, bind POST data
                ctx['education_formset'] = EducationFormSet(
                    self.request.POST, instance=self.object
                )
                ctx['experience_formset'] = ExperienceFormSet(
                    self.request.POST, instance=self.object
                )
            else:
                # If just viewing the page, load existing data
                ctx['education_formset'] = EducationFormSet(instance=self.object)
                ctx['experience_formset'] = ExperienceFormSet(instance=self.object)
        return ctx

    def form_valid(self, form):
        """
        This function saves the main form AND the formsets.
        """
        ctx = self.get_context_data()
        
        if self.request.user.profile.is_company:
            # If they are a company, just save the main form
            form.save()
            messages.success(self.request, "Profile updated successfully.")
            return super().form_valid(form)

        education_formset = ctx.get('education_formset')
        experience_formset = ctx.get('experience_formset')

        if (form.is_valid() and 
            education_formset and education_formset.is_valid() and 
            experience_formset and experience_formset.is_valid()):
            
            # Save the main profile form
            form.save()
            
            # Save the education formset
            education_formset.save()
            
            # Save the experience formset
            experience_formset.save()
            
            messages.success(self.request, "Profile updated successfully.")
            return redirect(self.success_url)
        else:
            # If any form or formset is invalid, show the errors
            messages.error(self.request, "Please correct the errors below.")
            return self.render_to_response(self.get_context_data(form=form))


class ForbiddenView(TemplateView):
    template_name = "accounts/forbidden.html"