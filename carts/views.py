from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from .models import Cart, Receiver, OrderedProduct
from users.models import Address
from products.models import Product
from django.contrib import messages
from .forms import *
from users.forms import AddressForm
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from conf import settings
import stripe
from django.utils import timezone
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.core.mail import EmailMultiAlternatives
from users.models import Action
from django.contrib.contenttypes.models import ContentType
from .tasks import send_receipt_email
from django.contrib.admin.views.decorators import staff_member_required
from coupons.forms import CouponApplyForm
from products.recommender import Recommender



@staff_member_required
def admin_cart_detail(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id)
    return render(request,
                'admin/carts/cart/detail.html',
                {'cart': cart})

class CartView(DetailView):
    model = Cart
    context_object_name = 'cart'
    template_name = 'carts/cart.html'
    
    def get_object(self, queryset = ...):
        if self.request.user.is_authenticated:
            receiver, _ = Receiver.objects.get_or_create(user= self.request.user)
            cart = Cart.objects.get_or_create_with_session(self.request, receiver = receiver, is_completed = False)
        else:
            if not self.request.session.session_key:
                self.request.session.create()
            session_key = self.request.session.session_key
            cart = Cart.objects.get_or_create_with_session(self.request, session_key = session_key, is_completed = False)
        # print(cart.coupon_id)
        return cart
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.get_object()
        disable_payment = False
        for ordered_product in cart.ordered.all():
            if ordered_product.quantity > ordered_product.product.quantity:
                disable_payment = True
                break
        context['title'] = 'Cart'
        context['disable_payment'] = disable_payment
        coupon_apply_form = CouponApplyForm()
        context['coupon_apply_form'] = coupon_apply_form

        r = Recommender()
        cart_products = [item.product for item in cart.ordered.all() if item.quantity > 0]
        if cart_products:
            recommended_products = r.suggest_products_for(cart_products, max_results=5)
        else:
            recommended_products = []
        context['recommended_products'] = recommended_products
        return context
    
    
def add_to_cart(request, product_slug):
    ordered_product = get_ordered_product(request, product_slug)
    if ordered_product.quantity >= ordered_product.product.quantity:
        messages.warning(request, 'We hava no such items left!')
    else:
        ordered_product.quantity += 1
        ordered_product.save()
    next_page = request.META.get('HTTP_REFERER', '/')
    return redirect(next_page)

def remove_from_cart(request, product_slug):
    ordered_product = get_ordered_product(request, product_slug)
    if ordered_product.quantity > 1:
        ordered_product.quantity -= 1
        ordered_product.save()
    next_page = request.META.get('HTTP_REFERER', '/')
    return redirect(next_page)   

def get_ordered_product(request, product_slug):
    product = Product.objects.get(slug=product_slug)
    if request.user.is_authenticated:
        receiver, _ = Receiver.objects.get_or_create(user= request.user)
        cart = Cart.objects.get_or_create_with_session(request, receiver = receiver, is_completed = False)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart = Cart.objects.get_or_create_with_session(request, session_key = session_key, is_completed = False)
    ordered_product, _ = OrderedProduct.objects.get_or_create(product=product, cart=cart)
    return ordered_product

def delete_full_item_from_cart(request, product_slug):
    ordered_product = get_ordered_product(request, product_slug)
    ordered_product.quantity = 0
    ordered_product.save()
    next_page = request.META.get('HTTP_REFERER', '/')
    return redirect(next_page) 

def reduce_quantity(request, ordered_product_pk):
    ordered_product = OrderedProduct.objects.get(pk=ordered_product_pk)
    ordered_product.quantity = ordered_product.product.quantity
    ordered_product.save()
    next_page = request.META.get('HTTP_REFERER', '/')
    return redirect(next_page) 


class CheckoutView(LoginRequiredMixin, View):
    template_name = 'carts/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = {}
        context['receiver_form'] = ReceiverCheckoutForm(instance=self.request.user.receiver)
        address_instance = self.request.user.receiver.address
        if address_instance:
            context['address_form'] = AddressForm(instance=address_instance)
        else:
            context['address_form'] = AddressForm()
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        receiver_form = ReceiverCheckoutForm(request.POST)
        address_form = AddressForm(request.POST)
        
        if receiver_form.is_valid() and address_form.is_valid():
            receiver = Receiver.objects.get(user=request.user)
            receiver_data = receiver_form.cleaned_data
            address_data = address_form.cleaned_data
            address, _ = Address.objects.get_or_create(**address_data)
            receiver_data['address'] = address
            for field, value in receiver_data.items():
                setattr(receiver, field, value)
            receiver.save()
            return redirect(reverse_lazy('carts:payment'))  
        else:
            error_messages = []
            for form_instance in [receiver_form, address_form]:
                for field, errors in form_instance.errors.items():
                    field_label = field if field != '__all__' else 'General'
                    error_messages.append(f"{field_label}: {', '.join(errors)}")
            full_error_message = "Please correct the following errors: " + "; ".join(error_messages)
            context = self.get_context_data()
            context['receiver_form'] = receiver_form
            context['address_form'] = address_form
            messages.error(request, full_error_message)
            return render(request, self.template_name, context)
        


stripe.api_key = settings.STRIPE_SECRET_KEY
class PaymentView(View):
    def get(self, request, *args, **kwargs):

        receiver, _ = Receiver.objects.get_or_create(user= self.request.user)
        cart = Cart.objects.get_or_create_with_session(request, receiver = receiver, is_completed = False)

        line_items = []
        order_description_parts = []

        for ordered_product in cart.ordered.all():
            if ordered_product.quantity > 0:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': ordered_product.product.title,
                        },
                        'unit_amount': int(ordered_product.product.full_price * 100),
                    },
                    'quantity': ordered_product.quantity,
                })
                order_description_parts.append(f"{ordered_product.product.title} x {ordered_product.quantity}")
        if cart.coupon:
            stripe_coupon = stripe.Coupon.create(name=cart.coupon.code, percent_off=cart.discount, duration='once')

        
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
    
# class PaymentSuccessView(TemplateView):
#     template_name = 'payment_success.html'

# class PaymentCancelView(TemplateView):
#     template_name = 'payment_cancel.html'


def payment_success(request):
    # receiver, _ = Receiver.objects.get_or_create(user= request.user)
    # cart, _ = Cart.objects.get_or_create(receiver = receiver, is_completed = False)
    # cart.is_completed = True
    # cart.date_completed = timezone.now().date()
    # for ordered_product in cart.ordered.all():
    #     product = ordered_product.product
    #     if ordered_product.price_at_purchase is None:
    #         ordered_product.price_at_purchase = product.full_price
    #         ordered_product.save()
    #     product.quantity -= ordered_product.quantity
    #     product.save()
    # cart.save()
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
    messages.success(request, 'Your payment was successful')
    # send_receipt_email.delay(request.user.email, cart.id, receiver.id)
    # create_action(request.user, 'purchased', product) 
    return redirect('main:index')

def payment_cancel(request):
    return redirect('carts:payment')




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