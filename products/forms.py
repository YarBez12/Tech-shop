from django import forms
from .models import Review



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('title', 'summary', 'pros', 'cons', 'grade')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your review title',
                'label': 'Title'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your review short description',
                'label': 'Summary'
            }),
            'pros': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your pros',
                'label': 'Pros'
            }),
            'cons': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your cons',
                'label': 'Cons'
            }),
            'grade': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': '3',
                'label': 'Grade'
            })
        }