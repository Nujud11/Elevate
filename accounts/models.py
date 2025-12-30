
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from wagtail.models import Page  # Not used here, but good practice
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet

User = get_user_model()

# --- File Upload Functions ---

def upload_avatar(instance, filename):
    return f"avatars/{instance.user_id}/{filename}"

def upload_cv(instance, filename):
    return f"cvs/{instance.user_id}/{filename}"

def upload_cover(instance, filename):
    return f"covers/{instance.user_id}/{filename}"

# --- Main Profile Model ---

class Profile(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("company", "Company"),
    ]

    GENDER_CHOICES = [
        ("female", "Female"),
        ("male", "Male"),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    full_name = models.CharField(max_length=150, blank=True)

    # shared
    bio = models.TextField(blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    language = models.CharField(max_length=255, blank=True) 
    avatar = models.ImageField(upload_to=upload_avatar, blank=True, null=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url  = models.URLField(blank=True)
    website_url  = models.URLField(blank=True)

    # student-only 
    cv = models.FileField(upload_to=upload_cv, blank=True, null=True)
    cover_letter = models.FileField(upload_to=upload_cover, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_student(self):
        return self.role == "student"

    @property
    def is_company(self):
        return self.role == "company"

    def get_absolute_url(self):
        return reverse("account_profile")

# --- Related "Child" Models for Formsets ---

class Education(models.Model):
    """
    This is a 'child' of the Profile model.
    A profile can have MANY education entries.
    """
    profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name="education"
    )
    
    # All fields are optional so blank forms will validate
    school_name = models.CharField(max_length=255, blank=True)
    degree = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank if you are still attending")

    class Meta:
        ordering = ['-end_date'] # Show newest first

    def __str__(self):
        # Add checks for None in case fields are blank
        return f"{self.degree or 'Degree'} at {self.school_name or 'School'}"


class Experience(models.Model):
    """
    This is also a 'child' of the Profile model.
    A profile can have MANY experiences.
    """
    profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name="experience"
    )
    
    # All fields are optional so blank forms will validate
    company_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date'] # Show newest first

    def __str__(self):
        # Add checks for None in case fields are blank
        return f"{self.role or 'Role'} at {self.company_name or 'Company'}"

