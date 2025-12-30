from django import forms
from internships.models import Internship

class InternshipForm(forms.ModelForm):
    class Meta:
        model = Internship
        fields = ["title","location","is_remote","description","requirements","deadline","is_active"]
        widgets = {
            "deadline": forms.DateInput(attrs={"type":"date"}),
            "description": forms.Textarea(attrs={"rows":5}),
            "requirements": forms.Textarea(attrs={"rows":4}),
        }


