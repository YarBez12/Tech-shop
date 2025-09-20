from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .utils import merge_carts  

@receiver(user_logged_in)
def merge_cart_on_login(sender, user, request, **kwargs):
    old_key = request.session.pop('anon_session_key', None)
    if old_key:
        merge_carts(old_key, user)