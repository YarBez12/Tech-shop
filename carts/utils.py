
from .models import Cart, Receiver, OrderedProduct
from products.models import Product


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
    for ordered_product in cart.ordered.all():
        if ordered_product.quantity > (ordered_product.product.quantity or 0):
            return True
    return False


def get_ordered_product(request, product_slug):
    product = Product.objects.get(slug=product_slug)
    cart = get_or_create_cart_for_request(request)
    ordered_product, _ = OrderedProduct.objects.get_or_create(product=product, cart=cart)
    return ordered_product