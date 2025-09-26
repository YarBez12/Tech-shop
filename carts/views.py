from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from .models import Cart, OrderedProduct
from users.models import Address
from products.models import Product
from django.contrib import messages
from .forms import *
from users.forms import AddressForm
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
import stripe
from xhtml2pdf import pisa
from users.models import Action
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.views.decorators import staff_member_required
from coupons.forms import CouponApplyForm
from products.recommender import Recommender
from users.utils import build_form_errors_html
from .utils import *
from products.utils.filters import get_prefetched_images_query

stripe.api_key = settings.STRIPE_SECRET_KEY


class CartView(DetailView):
    model = Cart
    context_object_name = 'cart'
    template_name = 'carts/cart.html'
    
    def get_object(self, queryset = ...):
        return get_or_create_cart_for_request(self.request)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.object.id
        cart = Cart.objects.prefetch_related('ordered__product').get(id=cart_id)
        context['title'] = 'Cart'
        context['disable_payment'] = cart_has_overstock(cart)
        context['coupon_apply_form'] = CouponApplyForm()

        r = Recommender()
        cart_products = [item.product for item in cart.ordered.all() if item.quantity > 0]
        context['recommended_products'] = r.suggest_products_for(cart_products, max_results=5) if cart_products else []
        return context
    

class CheckoutView(LoginRequiredMixin, View):
    template_name = 'carts/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = {}
        receiver = get_or_create_receiver(self.request)
        context['receiver_form'] = ReceiverCheckoutForm(instance=receiver)
        address_instance = receiver.address
        context['address_form'] = AddressForm(instance=address_instance) if address_instance else AddressForm()
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        receiver_form = ReceiverCheckoutForm(request.POST)
        address_form = AddressForm(request.POST)
        
        if receiver_form.is_valid() and address_form.is_valid():
            receiver = get_or_create_receiver(request)
            receiver_data = receiver_form.cleaned_data
            address_data = address_form.cleaned_data
            address, _ = Address.objects.get_or_create(**address_data)
            receiver_data['address'] = address
            for field, value in receiver_data.items():
                setattr(receiver, field, value)
            receiver.save()
            return redirect(reverse_lazy('carts:payment'))  
        else:
            messages.error(request, build_form_errors_html(receiver_form, address_form))
            context = self.get_context_data()
            context['receiver_form'] = receiver_form
            context['address_form'] = address_form
            return render(request, self.template_name, context)
        

class PaymentView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        receiver = get_or_create_receiver(request)
        cart = Cart.objects.get_or_create_with_session(request, receiver=receiver, is_completed=False)
        cart = Cart.objects.select_related('receiver').prefetch_related('ordered__product').get(pk=cart.pk)
        line_items, order_description_parts = [], []

        if cart.ordered.filter(quantity__gt=Coalesce(F('product__quantity'), 0)).exists():
            messages.warning(request, 'Adjust quantities to proceed to checkout')
            return redirect('carts:cart')

        for ordered_product in cart.ordered.all():
            if ordered_product.quantity > 0:
                product = ordered_product.product
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product.title,
                        },
                        'unit_amount': int(product.full_price * 100),
                    },
                    'quantity': ordered_product.quantity,
                })
                order_description_parts.append(f"{product.title} x {ordered_product.quantity}")
        
        session_data = {
            'payment_method_types': ['card'],
            'customer_email': request.user.email,
            'line_items': line_items,
            'mode': 'payment',
            'success_url': request.build_absolute_uri(reverse_lazy('carts:payment_success')) + "?session_id={CHECKOUT_SESSION_ID}",
            'cancel_url': request.build_absolute_uri(reverse_lazy('carts:payment_cancel')),
            'metadata': {
                'order_description': ", ".join(order_description_parts)
            }
        }
        if cart.coupon:
            stripe_coupon = stripe.Coupon.create(name=cart.coupon.code, percent_off=cart.discount, duration='once'
            )
            session_data['discounts'] = [{'coupon': stripe_coupon.id}]

        session = stripe.checkout.Session.create(**session_data)

        return redirect(session.url)
    
def payment_success(request):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
    messages.success(request, 'Your payment was successful')
    return redirect('main:index')

def payment_cancel(request):
    return redirect('carts:payment')
    
    
def add_to_cart(request, product_slug):
    ordered_product = get_ordered_product(request, product_slug)
    stock = ordered_product.product.quantity or 0
    if ordered_product.quantity >= stock:
        messages.warning(request, 'We have no such items left!')
    else:
        OrderedProduct.objects.filter(pk=ordered_product.pk).update(quantity=F('quantity') + 1)
    next_page = request.META.get('HTTP_REFERER', '/')
    return redirect(next_page)

def remove_from_cart(request, product_slug):
    ordered_product = get_ordered_product(request, product_slug)
    if ordered_product.quantity > 1:
        OrderedProduct.objects.filter(pk=ordered_product.pk).update(quantity=F('quantity') - 1)
    next_page = request.META.get('HTTP_REFERER', '/')
    return redirect(next_page)   

def delete_full_item_from_cart(request, product_slug):
    ordered_product = get_ordered_product(request, product_slug)
    OrderedProduct.objects.filter(pk=ordered_product.pk).update(quantity=0)
    next_page = request.META.get('HTTP_REFERER', '/')
    return redirect(next_page) 

def reduce_quantity(request, ordered_product_pk):
    ordered_product = OrderedProduct.objects.select_related('product').get(pk=ordered_product_pk)
    OrderedProduct.objects.filter(pk=ordered_product.pk).update(quantity=(ordered_product.product.quantity or 0))
    next_page = request.META.get('HTTP_REFERER', '/')
    return redirect(next_page) 


@staff_member_required
def admin_cart_detail(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id)
    return render(request,
                'admin/carts/cart/detail.html',
                {'cart': cart})
