from django import forms
from .models import Receiver
from users.forms import UserFieldsMixin

class ReceiverCheckoutForm(UserFieldsMixin):
    class Meta(UserFieldsMixin.Meta):
        model = Receiver
        fields = ('first_name', 'last_name', 'email', 'phone')
