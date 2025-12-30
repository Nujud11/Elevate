from django.urls import path
from .views import (
    CompanyAllApplicationsView,
    CompanyPostingsView,
    CompanyApplicationsView,
    InternshipCreateView,
    InternshipUpdateView,
    ApplicationStatusUpdateView,
    CompanyApplicationsCSVView,
)


urlpatterns = [
    # Postings CRUD
    path("internships/", CompanyPostingsView.as_view(), name="company_postings"), # Retained for backward compatibility
    path("internships/new/", InternshipCreateView.as_view(), name="company_create"),
    path("internships/<int:pk>/edit/", InternshipUpdateView.as_view(), name="company_edit"),

    # Applications for a specific posting
    path("internships/<int:pk>/applications/", CompanyApplicationsView.as_view(), name="company_applications"),

    path("applications/all/", CompanyAllApplicationsView.as_view(), name="company_all_applications"),
]

urlpatterns += [
    path("applications/<int:pk>/status/", ApplicationStatusUpdateView.as_view(), name="company_application_status"),
]


urlpatterns += [
    path(
        "internships/<int:pk>/applications/export/",
        CompanyApplicationsCSVView.as_view(),
        name="company_applications_export",
    ),
]


