from django.contrib.admin import SimpleListFilter
from django.contrib.auth import get_user_model
from wagtail_modeladmin.options import ModelAdmin
# Note: We do NOT import modeladmin_register here, 
# as it's registered by the InternshipGroup.
from .models import Application

User = get_user_model()

# --- Costom Filter by Company ---
class CompanyApplicationFilter(SimpleListFilter):
    """
    This custom filter only lists companies in the filter
    dropdown whose internships have received applications.
    """
    title = 'Company'  # The title of the filter box
    parameter_name = 'company'  # The URL parameter

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples (id, display_name) for the filter options.
        """
        # Get all companies that have internships which have received applications
        companies = User.objects.filter(
            profile__role='company', 
            owned_internships__applications__isnull=False
        ).distinct().order_by('username')
        
        return [(c.id, c.username) for c in companies]

    def queryset(self, request, queryset):
        """
        Applies the filter to the main application queryset.
        """
        if self.value():
            # Filter applications based on the internship's owner
            return queryset.filter(internship__owner_id=self.value())
        return queryset


class ApplicationAdmin(ModelAdmin):
    model = Application
    menu_label = "Applications"
    menu_icon = "form"
    
    list_display = ("internship", "student", "status", "submitted_at")
    
    list_filter = (CompanyApplicationFilter, "status", "internship")
    
    search_fields = ("student__username", "internship__title")
    ordering = ("-submitted_at",)