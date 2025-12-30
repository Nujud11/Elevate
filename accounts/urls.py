
# accounts/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    RegisterView, CustomLoginView, ForbiddenView,
    ProfileDetailView, ProfileUpdateView
)

urlpatterns = [
    path("register/",               RegisterView.as_view(), name="register"),
    path("login/",                  CustomLoginView.as_view(), name="login"),
    path("logout/",                 LogoutView.as_view(next_page="login"), name="logout"),

    path("forbidden/",              ForbiddenView.as_view(), name="forbidden"),
    

    path("profile/",                ProfileDetailView.as_view(), name="account_profile"),
    path("profile/edit/",           ProfileUpdateView.as_view(), name="account_profile_edit"),
    path("profile/user/<int:pk>/",  ProfileDetailView.as_view(), name="user_public_profile"), # FOR VIEWING OTHER USER PROFILES 
]


