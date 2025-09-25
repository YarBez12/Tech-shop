import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Cart, Receiver
from .tasks import send_receipt_email
from django.utils import timezone
from coupons.models import CouponUsage
from products.recommender import Recommender
from products.utils.actions import create_action
from django.db import transaction
from django.db.models import F, IntegerField, Value
from django.db.models.functions import Coalesce, Greatest
from products.models import Product



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    if not sig_header:
        return HttpResponse(status=400)
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET)
        
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)
    
    if event.type != 'checkout.session.completed':
        return HttpResponse(status=200)
    session = event.data.object
    email = session.get('customer_email')
    if session.get('mode') != 'payment' or session.get('payment_status') != 'paid' or not email:
        return HttpResponse(status=200)
    try:
        receiver = Receiver.objects.select_related('user').get(user__email=email)
    except Receiver.DoesNotExist:
        return HttpResponse(status=200)

    try:
        cart = Cart.objects.select_related('receiver').prefetch_related('ordered__product').get(receiver=receiver, is_completed=False)
    except Cart.DoesNotExist:
        return HttpResponse(status=200)
    
    if cart.is_completed or cart.stripe_id:
        return HttpResponse(status=200)
    
    with transaction.atomic():
        for ordered_product in cart.ordered.select_related('product').all():
            product = ordered_product.product
            if not product:
                continue
            if ordered_product.price_at_purchase is None:
                ordered_product.price_at_purchase = product.full_price
                ordered_product.save(update_fields=['price_at_purchase'])
            Product.objects.filter(pk=ordered_product.product_id).update(
                quantity=Greatest(
                    Value(0),
                    Coalesce(F('quantity'), Value(0), output_field=IntegerField()) - (ordered_product.quantity or 0)
                )
            )
        cart.stripe_id = session.get('payment_intent')
        cart.is_completed = True
        cart.date_completed = timezone.now().date()
        cart.save(update_fields=['is_completed', 'date_completed', 'stripe_id'])
        if cart.coupon:
            coupon = cart.coupon
            coupon.used_count = (coupon.used_count or 0) + 1
            if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
                coupon.active = False
            coupon.save(update_fields=['used_count', 'active'])
            if receiver.user:
                CouponUsage.objects.get_or_create(user=receiver.user, coupon=cart.coupon)

    products = [item.product for item in cart.ordered.all() if item.product]
    if products:
        r = Recommender()
        r.products_bought(products)
    
    if receiver.user:
        send_receipt_email.delay(receiver.user.email, cart.id, receiver.id)
        for p in products:
            create_action(receiver.user, 'purchased', p)
        

    
    return HttpResponse(status=200)


