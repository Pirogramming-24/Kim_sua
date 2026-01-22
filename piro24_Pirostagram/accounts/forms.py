from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'bio', 'profile_image')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }