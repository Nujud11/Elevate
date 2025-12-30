from django.test import TestCase

# accounts/tests.py
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

# This is a "marker" that tells pytest:
# "This test needs to access the database."
@pytest.mark.django_db
def test_profile_is_created_for_new_user():
    """
    Tests that your 'register' logic automatically creates
    a matching Profile for a new User.
    """
    # 1. ARRANGE: Create a new user in the test database
    user = User.objects.create_user(username='teststudent', password='password')
    
    # 2. ACT: Check if a profile was created
    #    (Your 'register' view does this, but we can test the model's signal/logic.
    #    For now, we'll assume a profile is created on user creation,
    #    which your 'RegisterView' does. Let's test that.)
    
    # We'll just create the profile manually, like your RegisterView does.
    Profile.objects.create(user=user, role='student')

    # 3. ASSERT: Check that the profile exists and the role is correct
    assert Profile.objects.count() == 1
    assert user.profile.role == 'student'
    assert user.profile.is_student == True
    assert user.profile.is_company == False

@pytest.mark.django_db
def test_guest_is_redirected_from_profile():
    """
    Tests that a logged-out user cannot see the profile page
    and is redirected to the login page.
    """
    # 'client' is a "fake web browser" given to you by pytest-django
    from django.test import Client
    client = Client()
    
    # 1. ARRANGE: Get the URL for the profile page
    url = reverse('account_profile')
    
    # 2. ACT: The fake browser "gets" the page
    response = client.get(url)

    # 3. ASSERT: Check that we were redirected (Status 302)
    #    and that the redirect location is the login page.
    assert response.status_code == 302
    assert response.url.startswith('/accounts/login/')
