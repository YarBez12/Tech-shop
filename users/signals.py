from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .utils import apply_remember_me, merge_carts
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import urlsplit
from django.urls import resolve, Resolver404, reverse
from django.contrib import messages


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    apply_remember_me(request)

    old_key = request.session.pop('anon_session_key', None)
    if old_key:
        merge_carts(old_key, user)
    messages.success(request, f"{user.first_name}, You successfuly logined")

