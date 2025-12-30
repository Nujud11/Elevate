# applications/models.py
from django.db import models
from internships.models import Internship
from django.contrib.auth import get_user_model
import os # Import os to get the file extension

User = get_user_model()

def get_application_cv_path(instance, filename):
    #media/applications/internship_12/student_123/cv.pdf
    ext = os.path.splitext(filename)[1]
    return f"applications/internship_{instance.internship.id}/student_{instance.student.id}/cv{ext}"

def get_application_cover_path(instance, filename):
    #media/applications/internship_12/student_123/cover_letter.pdf
    ext = os.path.splitext(filename)[1]
    return f"applications/internship_{instance.internship.id}/student_{instance.student.id}/cover_letter{ext}"


class Application(models.Model):

    STATUS_CHOICES = [
        ('new', 'New'),
        ('review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name="applications")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    submitted_at = models.DateTimeField(auto_now_add=True)

    cv = models.FileField(upload_to=get_application_cv_path, blank=True, null=True)
    cover_letter = models.FileField(upload_to=get_application_cover_path, blank=True, null=True)

    def __str__(self):
        return f"{self.student.username}'s application for {self.internship.title}"

    class Meta:
        ordering = ['-submitted_at']