from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Internship(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_internships")
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=150, blank=True)
    is_remote = models.BooleanField(default=False)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"
