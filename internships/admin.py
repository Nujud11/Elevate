from django.contrib import admin
from .models import Internship

@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "is_active", "posted_at", "deadline")
    list_filter = ("is_active", "is_remote")
    search_fields = ("title", "description", "requirements", "location")
