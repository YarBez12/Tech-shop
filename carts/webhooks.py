import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Cart, Receiver
from .tasks import send_receipt_email
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from users.models import Action


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET)
        
    except ValueError as e:
        return HttpResponse(status=400)
    
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    
    if event.type == 'checkout.session.completed':
        session = event.data.object
        email = session.get('customer_email')
        if session.mode == 'payment' and session.payment_status == "paid":
            try:
                receiver = Receiver.objects.get(user__email=email)
                cart = Cart.objects.get(receiver=receiver, is_completed=False)
            except Receiver.DoesNotExist:
                return HttpResponse(status=404)
            
            cart.is_completed = True
            cart.date_completed = timezone.now().date()
            for ordered_product in cart.ordered.all():
                product = ordered_product.product
                if ordered_product.price_at_purchase is None:
                    ordered_product.price_at_purchase = product.full_price
                    ordered_product.save()
                product.quantity -= ordered_product.quantity
                product.save()
            cart.stripe_id = session.payment_intent
            cart.save()
            send_receipt_email.delay(receiver.user.email, cart.id, receiver.id)
            create_action(receiver.user, 'purchased', product) 
        

    
    return HttpResponse(status=200)

def create_action(user, verb, target=None):
    existing = Action.objects.filter(user=user, verb=verb)
    if target:
        ct = ContentType.objects.get_for_model(target)
        existing = existing.filter(target_ct=ct, target_id=target.id)
    if existing.exists():
        return False

    action = Action(user=user, verb=verb, target=target)
    action.save()
    return True

