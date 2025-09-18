from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from users.models import Address, User
from products.models import Product
import uuid
from django.utils import timezone
from decimal import Decimal
from django.conf import settings
from coupons.models import Coupon
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class Receiver(models.Model):
    first_name = models.CharField(_('first_name'), max_length=200)
    last_name = models.CharField(_('last_name'),max_length=200)
    phone = PhoneNumberField(_('phone'),blank=True, null=True)
    email = models.EmailField(_('email'),)
    user = models.OneToOneField(User, verbose_name=_('user'), on_delete=models.SET_NULL, null=True, blank=True, related_name='receiver')
    address = models.ForeignKey(Address, verbose_name=_('address'), on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if self.user and self._state.adding:
            if not self.first_name:
                self.first_name = self.user.first_name
            if not self.last_name:
                self.last_name = self.user.last_name
            if not self.phone:
                self.phone = self.user.phone
            if not self.email:
                self.email = self.user.email
            if not self.address:
                self.address = self.user.address
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class CartManager(models.Manager):
    def create_with_session(self, request, **kwargs):
        coupon_id = request.session.get('coupon_id')
        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)
                kwargs['coupon'] = coupon
                kwargs['discount'] = coupon.discount
            except Coupon.DoesNotExist:
                pass 
        return self.create(**kwargs)
    
    def get_or_create_with_session(self, request, **kwargs):
        if not request.session.session_key:
            request.session.create()
        cart, created = self.get_or_create(**kwargs)
        session_coupon_id = request.session.get('coupon_id')
        if created:
            cart.session_key = request.session.session_key
        if session_coupon_id:
            try:
                coupon = Coupon.objects.get(id=session_coupon_id)
                if cart.coupon != coupon:
                    cart.coupon = coupon
                    cart.discount = coupon.discount
                    cart.save()
            except Coupon.DoesNotExist:
                pass
        return cart

class Cart(models.Model):
    receiver = models.ForeignKey(Receiver, on_delete=models.SET_NULL, blank=True, null=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    date_completed = models.DateField(null=True, blank=True)
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    stripe_id = models.CharField(max_length=250, blank=True)

    coupon = models.ForeignKey(Coupon, related_name='orders', null=True, blank=True, on_delete=models.SET_NULL)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    objects = CartManager()



    def save(self, *args, **kwargs):
        if not self.order_number or self.order_number.strip() == "":
            date_str = timezone.now().strftime("%Y%m%d")
            unique_code = uuid.uuid4().hex[:6].upper()
            self.order_number = f"{date_str}-{unique_code}"
        super().save(*args, **kwargs)

    @property
    def cart_total_price(self):
        order_products = self.ordered.all()
        total_price = sum([product.total_price for product in order_products])
        return round(total_price, 2)

    @property
    def cart_total_quantity(self):
        order_products = self.ordered.all()
        total_quantity = sum([product.quantity for product in order_products])
        return total_quantity
    
    def __str__(self):
        if self.receiver:
            return self.receiver.first_name
        return str(self.session_key)
    
    def get_stripe_url(self):
        if not self.stripe_id:
            return ''
        if '_test_' in settings.STRIPE_SECRET_KEY:
            path = '/test/'
        else:
            path = '/'
        return f'https://dashboard.stripe.com{path}payments/{self.stripe_id}'
    
    @property
    def cart_discount(self):
        if self.discount:
            return (self.discount / Decimal(100)) * self.cart_total_price
        return Decimal(0)
    
    @property
    def cart_total_price_after_discount(self):
        return self.cart_total_price - self.cart_discount

class OrderedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='ordered')
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, related_name='ordered')
    quantity = models.IntegerField(default=0, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.product.title
    
    @property
    def total_price(self):
        if self.price_at_purchase is not None:
            return round(self.price_at_purchase * Decimal(self.quantity), 2)
        return round(Decimal(self.product.full_price) * Decimal(self.quantity),2)