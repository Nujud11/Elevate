
from django import forms

class ContactForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-input'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False, # Phone number is optional in your screenshot
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number', 'class': 'form-input'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-input'})
    )
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Message', 'rows': 5, 'class': 'form-textarea'})
    )

  