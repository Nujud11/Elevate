# applications/forms.py
from django import forms
from .models import Application

class ApplicationCreateForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["cv", "cover_letter"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cv'].required = True

    def clean_cv(self):
        f = self.cleaned_data.get("cv")
        
        # Check if a file was actually uploaded
        if not f:
            raise forms.ValidationError("This field is required.") 
        if f.size > 5 * 1024 * 1024:  # 5MB
            raise forms.ValidationError("CV must be ≤ 5 MB.")
        if not f.name.lower().endswith((".pdf", ".doc", ".docx")):
            raise forms.ValidationError("Only PDF/DOC/DOCX allowed.")
        return f

    
    def clean_cover_letter(self):
        f = self.cleaned_data.get("cover_letter")
        if f: # Check if a file was uploaded (it's optional)
            if f.size > 2 * 1024 * 1024: # Example: 2MB limit
                raise forms.ValidationError("Cover Letter must be ≤ 2 MB.")
            if not f.name.lower().endswith((".pdf", ".doc", ".docx")):
                 raise forms.ValidationError("Only PDF/DOC/DOCX allowed.")
        return f
    
class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["status"]



