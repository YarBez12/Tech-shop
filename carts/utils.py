
from .models import Cart, Receiver, OrderedProduct
from products.models import Product
from django.db.models import F
from django.db.models.functions import Coalesce


def get_or_create_receiver(request):
    return Receiver.objects.get_or_create(user=request.user)[0]

def get_or_create_cart_for_request(request, *, receiver=None):
    if receiver is not None:
        return Cart.objects.get_or_create_with_session(request, receiver=receiver, is_completed=False)
    if request.user.is_authenticated:
        receiver = get_or_create_receiver(request)
        return Cart.objects.get_or_create_with_session(request, receiver=receiver, is_completed=False)
    if not request.session.session_key:
        request.session.create()
    return Cart.objects.get_or_create_with_session(request, session_key=request.session.session_key, is_completed=False)

def cart_has_overstock(cart):
    return cart.ordered.select_related('product').filter(
        quantity__gt=Coalesce(F('product__quantity'), 0)
    ).exists()


def get_ordered_product(request, product_slug):
    cart = get_or_create_cart_for_request(request)
    product = (Product.objects
               .only('id', 'slug', 'title', 'quantity', 'price', 'discount')
               .get(slug=product_slug))
    ordered_product, _ = OrderedProduct.objects.get_or_create(
        product=product, cart=cart, defaults={'quantity': 0}
    )
    return ordered_product