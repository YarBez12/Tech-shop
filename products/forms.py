from django import forms
from .models import Review, Product
from taggit.forms import TagWidget




class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('title', 'summary', 'pros', 'cons', 'grade')
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Your review title',
                'label': 'Title'
            }),
            'summary': forms.Textarea(attrs={
                'placeholder': 'Your review short description',
                'label': 'Summary'
            }),
            'pros': forms.Textarea(attrs={
                'placeholder': 'Your pros',
                'label': 'Pros'
            }),
            'cons': forms.Textarea(attrs={
                'placeholder': 'Your cons',
                'label': 'Cons'
            }),
            'grade': forms.NumberInput(attrs={
                'value': '3',
                'label': 'Grade'
            })
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('title', 'summary', 'description', 'price', 'discount', 'quantity', 'warranty', 'category', 'brand', 'tags')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Product title'}),
            'summary': forms.TextInput(attrs={'placeholder': 'Short summary'}),
            'description': forms.Textarea(attrs={'placeholder': 'Full description'}),
            'price': forms.NumberInput(attrs={'min': 0}),
            'discount': forms.NumberInput(attrs={'min': 0, 'max': 100}),
            'quantity': forms.NumberInput(attrs={'min': 1}),
            'warranty': forms.NumberInput(attrs={'min': 0}),
            'category': forms.Select(),  
            'brand': forms.Select(),     
            'tags': TagWidget(attrs={'placeholder': 'Enter tags separated by commas, e.g. iphone, samsung'}) 
        }
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m() 
        return instance
        