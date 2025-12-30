from wagtail_modeladmin.options import (
    ModelAdmin, modeladmin_register
)
from .models import Profile

class ProfileAdmin(ModelAdmin):
    model = Profile
    menu_label = "Profiles"
    menu_icon = "user"
    menu_order = 199  # (Just under Internship System)
    
    # Fields to display in the list view
    list_display = ("user", "full_name", "role")
    
    # Fields to allow filtering on
    list_filter = ("role", "gender", "language")
    
    # Fields to enable searching on
    search_fields = ("full_name", "user__username", "user__email", "bio")

# Register the new admin
modeladmin_register(ProfileAdmin)