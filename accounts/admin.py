from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "full_name")  #'bio', 'gender', 'language', 'avatar', 'linkedin_url', 'twitter_url', 'website_url', 'cv', 'cover_letter'
    search_fields = ("user__username", "role", "full_name")
    list_filter = ("role",)

