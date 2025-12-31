from django import forms
from .models import MovieReview

class MovieReviewForm(forms.ModelForm):
    class Meta:
        model = MovieReview
        fields = ['title', 'year', 'director', 'actors', 'genre', 'rating', 'runtime', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows':4, 'cols':40}),
            'rating': forms.NumberInput(attrs={'min':0, 'max':5, 'step':0.1}),
            'year': forms.NumberInput(attrs={'min':1900, 'max':2100}),
            'runtime': forms.NumberInput(attrs={'min':1}),
        }
