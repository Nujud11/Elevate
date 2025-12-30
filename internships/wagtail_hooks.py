from django.contrib.admin import SimpleListFilter
from django.contrib.auth import get_user_model
from wagtail_modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register
)
from .models import Internship
from applications.wagtail_hooks import ApplicationAdmin 

User = get_user_model()

# ---  CUSTOM FILTER ---
class CompanyOwnerFilter(SimpleListFilter):
    """
    This custom filter only lists users in the filter
    dropdown who have the 'company' role in their profile.
    """
    title = 'Company'  # The title of the filter box
    parameter_name = 'company_owner'  # The URL parameter

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples (id, display_name)
        for the filter options.
        """
        # Get all users who are companies and own at least one internship
        companies = User.objects.filter(
            profile__role='company', 
            owned_internships__isnull=False
        ).distinct().order_by('username')
        
        # Create the list of (id, username) tuples
        return [(c.id, c.username) for c in companies]

    def queryset(self, request, queryset):
        """
        Applies the filter to the main queryset.
        """
        if self.value():
            # If a company ID is selected, filter the internships
            return queryset.filter(owner_id=self.value())
        return queryset

class InternshipAdmin(ModelAdmin):
    model = Internship
    menu_label = "Internships"
    menu_icon = "briefcase"
    
    list_display = ("title", "owner", "location", "is_remote", "deadline", "is_active")
    
    list_filter = (CompanyOwnerFilter, "is_remote", "is_active", "location")
    
    search_fields = ("title", "owner__username", "location", "description")

class InternshipGroup(ModelAdminGroup):
    menu_label = "Internship System"
    menu_icon = "folder-open-inverse"
    menu_order = 200
    items = (InternshipAdmin, ApplicationAdmin) 

modeladmin_register(InternshipGroup)