from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User, Address
from phonenumber_field.formfields import PhoneNumberField

def attributes(attrs=None):
    base = {'class': 'form-control'}
    if attrs: 
        base.update(attrs)
    return base

class UserFieldsMixin(forms.ModelForm):
    first_name = forms.CharField(
        label=('First name(s)'),
        widget=forms.TextInput(attrs=attributes({'autofocus': True, 'placeholder': 'Enter your first name(s)'}))
    )
    last_name = forms.CharField(
        label=('Last name(s)'),
        widget=forms.TextInput(attrs=attributes({'placeholder': 'Enter your last name(s)'}))
    )
    email = forms.EmailField(
        label=('Email'),
        widget=forms.EmailInput(attrs=attributes({'placeholder': 'Enter your email', 'autocomplete': 'email'}))
    )
    phone = PhoneNumberField(
        label=('Phone'),
        required=False,
        region='IE', 
        widget=forms.TextInput(attrs=attributes({'placeholder': 'Enter your phone number', 'autocomplete': 'tel'}))
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone')

class LoginForm(AuthenticationForm):

    username = forms.EmailField(
        label='Email',
        widget = forms.EmailInput(attrs= {'autofocus': True, 'placeholder': 'Enter your email', 'autocomplete': 'username'})
    )
    password = forms.CharField(
        label='Password',
        widget = forms.PasswordInput(attrs= {'placeholder': 'Enter your password', 'autocomplete': 'current-password'})
    )

class UserRegistrationForm(UserFieldsMixin, UserCreationForm):
    password1 = forms.CharField(
        label='Password',
        widget = forms.PasswordInput(attrs= attributes({'placeholder': 'Enter your password', 'autocomplete': 'new-password'}))
    )
    password2 = forms.CharField(
        label='Confirm your password',
        widget = forms.PasswordInput(attrs= attributes({'placeholder': 'Confirm your password', 'autocomplete': 'new-password'}))
    )

    class Meta(UserFieldsMixin.Meta):
        fields = UserFieldsMixin.Meta.fields + ('password1', 'password2')

class UserEditForm(UserFieldsMixin):
    class Meta(UserFieldsMixin.Meta):
        pass

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('address_field1', 'address_field2', 'city', 'state', 'country', 'postal_code')
        widgets = {
            'address_field1': forms.TextInput(attrs= attributes({'placeholder': 'Address', 'autocomplete': 'address-line1'})),
            'address_field2': forms.TextInput(attrs= attributes({'placeholder': 'Additional address', 'autocomplete': 'address-line2'})),
            'city': forms.TextInput(attrs= attributes({'placeholder': 'City', 'autocomplete': 'address-level2'})),
            'state': forms.TextInput(attrs= attributes({'placeholder': 'State', 'autocomplete': 'address-level1'})),
            'country': forms.TextInput(attrs= attributes({'placeholder': 'Country', 'autocomplete': 'country'})),
            'postal_code': forms.TextInput(attrs= attributes({'placeholder': 'Postcode', 'autocomplete': 'postal-code'}))
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
        widget=forms.TextInput(attrs=attributes({'placeholder': 'Subject'})),
        label="Subject"
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs=attributes({'placeholder': 'Enter your message in plain text'})),
        label="Message (Plain Text)"
    )
    html_message = forms.CharField(
        widget=forms.Textarea(attrs=attributes({'placeholder': 'Enter your HTML message (optional)'})),
        required=False,
        label="HTML Message"
    )
