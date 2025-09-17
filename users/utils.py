import redis
from django.conf import settings
from django.utils.html import escape
from django.utils.safestring import mark_safe
from carts.models import Cart, Receiver
from django.db import transaction


r = redis.Redis.from_url(settings.REDIS_URL)

def get_user_favourites(user_id):
    return r.smembers(f'favourite:user:{user_id}')

def apply_remember_me(request):
    remember_me = request.POST.get('remember_me')
    if remember_me:
        request.session.cycle_key()
        request.session.set_expiry(60 * 60 * 24 * 30)
    else:
        request.session.set_expiry(0)

def build_form_errors_html(*forms, title="Please correct the following errors:"):
    error_messages = []

    def label_for(form, field_name):
        if field_name == '__all__':
            return 'General'
        f = form.fields.get(field_name)
        return f.label if f and f.label else field_name

    for form in forms:
        if not form:
            continue
        for field_name, errors in form.errors.items():
            label = escape(label_for(form, field_name))
            for err in errors:
                error_messages.append(f"<li><strong>{label}</strong>: {escape(err)}</li>")

    if not error_messages:
        return ""

    full_error_message = (
        f"<div>{escape(title)}</div>"
        "<ul class='ui list' style='margin:.5em 0 0'>"
        + "".join(error_messages) +
        "</ul>"
    )
    return mark_safe(full_error_message)


@transaction.atomic
def merge_carts(session_key, user):
    if not session_key:
        return
    try:
        session_cart = Cart.objects.select_related('receiver').prefetch_related('ordered__product').get(
            session_key=session_key, is_completed=False
        )
    except Cart.DoesNotExist:
        return
    
    receiver, _ = Receiver.objects.get_or_create(user=user)
    try:
        user_cart = Cart.objects.get(receiver = receiver, is_completed = False)
    except (Cart.DoesNotExist):
        user_cart = None
        session_cart.receiver = receiver
        session_cart.session_key = None
        session_cart.save(update_fields=['receiver', 'session_key'])
        return

    for ordered_product in session_cart.ordered.all():
        user_ordered_product, created = user_cart.ordered.get_or_create(product=ordered_product.product)
        if not created:
            user_ordered_product.quantity += ordered_product.quantity
        else:
            user_ordered_product.quantity = ordered_product.quantity
        user_ordered_product.save()
    session_cart.delete()