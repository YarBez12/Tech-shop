from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from .models import User, Address
from phonenumber_field.formfields import PhoneNumberField

class LoginForm(AuthenticationForm):

    username = forms.EmailField(label='Email',
                             widget = forms.EmailInput(attrs= {
                                 'autofocus': True,
                                 'class': 'form-control',
                                 'placeholder': 'Enrer your email'
                             }))
    password = forms.CharField(label='Password',
                             widget = forms.PasswordInput(attrs= {
                                 'autocomplete': 'current-password',
                                 'class': 'form-control',
                                 'placeholder': 'Enrer your password'
                             }))

    class Meta:
        model = User
        fields = ('username', 'password')

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label='First name(s)',
                             widget = forms.TextInput(attrs= {
                                 'autofocus': True,
                                 'class': 'form-control',
                                 'placeholder': 'Enrer your first name(s)'
                             }))
    last_name = forms.CharField(label='Last name(s)',
                             widget = forms.TextInput(attrs= {
                                 'class': 'form-control',
                                 'placeholder': 'Enrer your last name(s)'
                             }))
    email = forms.EmailField(label='Email',
                             widget = forms.EmailInput(attrs= {
                                 'class': 'form-control',
                                 'placeholder': 'Enrer your email'
                             }))
    phone = PhoneNumberField(
        label='Phone',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )
    password1 = forms.CharField(label='Password',
                             widget = forms.PasswordInput(attrs= {
                                 'class': 'form-control',
                                 'placeholder': 'Enrer your password'
                             }))
    password2 = forms.CharField(label='Confirm your password',
                             widget = forms.PasswordInput(attrs= {
                                 'class': 'form-control',
                                 'placeholder': 'Confirm your password'
                             }))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'password1', 'password2')

class UserEditForm(forms.ModelForm):
    first_name = forms.CharField(label='First name(s)',
                             widget = forms.TextInput(attrs= {
                                 'autofocus': True,
                                 'class': 'form-control',
                                 'placeholder': 'Enrer your first name(s)'
                             }))
    last_name = forms.CharField(label='Last name(s)',
                             widget = forms.TextInput(attrs= {
                                 'class': 'form-control',
                                 'placeholder': 'Enrer your last name(s)'
                             }))
    email = forms.EmailField(label='Email',
                             widget = forms.EmailInput(attrs= {
                                 'class': 'form-control',
                                 'placeholder': 'Enrer your email'
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
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone')

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('address_field1', 'address_field2', 'city', 'state', 'country', 'postal_code')
        widgets = {
            'address_field1': forms.TextInput(attrs= {
                'class': 'form-control',
                'placeholder': 'Address'
            }),
            'address_field2': forms.TextInput(attrs= {
                'class': 'form-control',
                'placeholder': 'Additional address'
            }),
            'city': forms.TextInput(attrs= {
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs= {
                'class': 'form-control',
                'placeholder': 'State'
            }),
            'country': forms.TextInput(attrs= {
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'postal_code': forms.TextInput(attrs= {
                'class': 'form-control',
                'placeholder': 'Postcode'
            })
        }
        labels = {
            'address_field1': 'Address',
            'address_field2': 'Additional address',
            'city': 'City',
            'state': 'State',
            'country': 'Country',
            'postal_code': 'Postcode'
        }
    

class MailForm(forms.Form):
    subject = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject'
        }),
        label="Subject"
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your message in plain text'
        }),
        label="Message (Plain Text)"
    )
    html_message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your HTML message (optional)'
        }),
        required=False,
        label="HTML Message"
    )

    