from django import forms
from .models import Receiver
from phonenumber_field.formfields import PhoneNumberField

class ReceiverCheckoutForm(forms.ModelForm):
    first_name = forms.CharField(label='First name(s)',
                             widget = forms.TextInput(attrs= {
                                 'autofocus': True,
                                 'class': 'form-control',
                                 'placeholer': 'Enrer your first name(s)'
                             }))
    last_name = forms.CharField(label='Last name(s)',
                             widget = forms.TextInput(attrs= {
                                 'class': 'form-control',
                                 'placeholer': 'Enrer your last name(s)'
                             }))
    email = forms.EmailField(label='Email',
                             widget = forms.EmailInput(attrs= {
                                 'class': 'form-control',
                                 'placeholer': 'Enrer your email'
                             }))
    
    phone = PhoneNumberField(
        label='Phone',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )

    class Meta:
        model = Receiver
        fields = ('first_name', 'last_name', 'email', 'phone')