# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory

from .models import Profile, Education, Experience

# ---------- 1. Registration Form ----------
class RegisterForm(UserCreationForm):
    ROLE_CHOICES = [("student", "Student"), ("company", "Company")]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "role"]
    def save(self, commit=True):
        user = super().save(commit=commit)
        Profile.objects.get_or_create(user=user)
        Profile.objects.filter(user=user).update(role=self.cleaned_data["role"])
        return user

# ---------- 2. Main Profile Forms ----------
INPUT_CLS = {"class": "input"}
TEXTAREA_CLS = {"class": "textarea", "rows": 5}
class BaseProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "full_name", "avatar", "bio", "linkedin_url", "twitter_url",
            "website_url", "language", "gender", "cv", "cover_letter",
        ]
        widgets = {
            "full_name":   forms.TextInput(attrs={**INPUT_CLS, "placeholder": "Your name"}),
            "bio":         forms.Textarea(attrs={**TEXTAREA_CLS, "placeholder": "Tell us a little about you…"}),
            "linkedin_url":forms.URLInput(attrs={**INPUT_CLS, "placeholder": "https://www.linkedin.com/in/…"}),
            "twitter_url": forms.URLInput(attrs={**INPUT_CLS, "placeholder": "https://x.com/username"}),
            "website_url": forms.URLInput(attrs={**INPUT_CLS, "placeholder": "https://your-portfolio.com"}),
            "gender":      forms.Select(attrs=INPUT_CLS),
            "language":    forms.TextInput(attrs={**INPUT_CLS, "placeholder": "e.g., English, Arabic"}),
        }
    def __init__(self, *args, **kwargs):
        role = kwargs.pop("role", None)
        super().__init__(*args, **kwargs)
        if "cv" in self.fields: self.fields["cv"].required = False
        if "cover_letter" in self.fields: self.fields["cover_letter"].required = False
        if "gender" in self.fields: self.fields["gender"].required = False
        if role == "company" or (hasattr(self.instance, "is_company") and self.instance.is_company):
            for f in ("cv", "cover_letter","gender"):
                self.fields.pop(f, None)

class StudentProfileForm(BaseProfileForm): pass
class CompanyProfileForm(BaseProfileForm):
    def __init__(self, *args, **kwargs):
        kwargs["role"] = "company"
        super().__init__(*args, **kwargs)

# --- WE ARE DELETING THE SAUDI_UNIVERSITIES LIST ---


# ---------- 3. Student Profile Formsets ----------

EducationFormSet = inlineformset_factory(
    Profile,
    Education,
    fields=('school_name', 'degree', 'start_date', 'end_date'),
    
    extra=2,    
    max_num=2,  
    min_num=0,  
    
    can_delete=True,
    widgets={
        'school_name': forms.TextInput(attrs={'placeholder': 'University Name'}),
        'degree': forms.TextInput(attrs={'placeholder': 'B.S. in Computer Science'}),
        'start_date': forms.DateInput(attrs={'type': 'date'}),
        'end_date': forms.DateInput(attrs={'type': 'date'}),
    }
)

ExperienceFormSet = inlineformset_factory(
    Profile,
    Experience,
    fields=('company_name', 'role', 'start_date', 'end_date', 'description'),

    extra=3,
    max_num=3,
    min_num=0,
    
    
    can_delete=True,
    widgets={
        'company_name': forms.TextInput(attrs={'placeholder': 'Company Name'}),
        'role': forms.TextInput(attrs={'placeholder': 'Software Engineer Intern'}),
        'start_date': forms.DateInput(attrs={'type': 'date'}),
        'end_date': forms.DateInput(attrs={'type': 'date'}),
        'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your role...'}),
    }
)