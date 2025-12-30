from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("internship", "student", "status", "submitted_at")
    list_filter = ("status",)
    search_fields = ("student__username", "internship__title")
