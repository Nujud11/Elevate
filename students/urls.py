
#students/urls.py
from django.urls import path
from django.views.generic.base import RedirectView

from .views import  (StudentBrowseView,
                      StudentDetailView, StudentApplyView,
                        StudentApplicationsView )


urlpatterns = [
    # Redirect old '/s/internships/' path to the new '/s/opportunities/'
    path("internships/", RedirectView.as_view(pattern_name='student_browse', permanent=True)),

    # Public browse page is now the root of /s/opportunities/
    path("opportunities/", StudentBrowseView.as_view(), name="student_browse"),
    
    # Applications list
    path("applications/", StudentApplicationsView.as_view(), name="student_apps"),
    
    # Detail page is nested under opportunities/ 
    path("opportunities/<int:pk>/", StudentDetailView.as_view(), name="student_detail"),
    
    # Apply form is nested under opportunities/
    path("opportunities/<int:pk>/apply/", StudentApplyView.as_view(), name="student_apply"),
]