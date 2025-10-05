from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from users.models import Address, User
from products.models import Product, ProductImage
import uuid
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from coupons.models import Coupon
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import Coalesce
from functools import cached_property
from django.db.models import DecimalField, ExpressionWrapper, Sum, Value, Prefetch, F
from django.db.models.functions import Coalesce, Cast, Round

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
    
class CartQuerySet(models.QuerySet):
    def with_totals(self):
        price_per_item = models.Case(
            models.When(
                ordered__price_at_purchase__isnull=False,
                then=F('ordered__price_at_purchase'),
            ),
            default=ExpressionWrapper(
                F('ordered__product__price') * (
                    Value(Decimal('1')) - (
                        ExpressionWrapper(
                            Cast(Coalesce(F('ordered__product__discount'), Value(0)),
                                 DecimalField(max_digits=5, decimal_places=2))
                            / Value(Decimal('100')),
                            output_field=DecimalField(max_digits=6, decimal_places=4),
                        )
                    )
                ),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            ),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )


        row_total = ExpressionWrapper(
            price_per_item * models.F('ordered__quantity'),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )

        return self.annotate(
            items_total=Coalesce(
                Sum(row_total),
                Value(Decimal('0')),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        ).annotate(
            discount_decimal=ExpressionWrapper(
                Cast(Coalesce(F('discount'), Value(0)),
                     DecimalField(max_digits=5, decimal_places=2))
                / Value(Decimal('100')),
                output_field=DecimalField(max_digits=6, decimal_places=4),
            ),
        ).annotate(
            total_raw=ExpressionWrapper(
                F('items_total') * (Value(Decimal('1')) - F('discount_decimal')),
                output_field=DecimalField(max_digits=12, decimal_places=6),
            ),
        ).annotate(
            total_after_discount=Round(
                Cast(F('total_raw'), DecimalField(max_digits=12, decimal_places=6)),
                precision=2,
            ),
        )
class CartManager(models.Manager):
    def get_queryset(self):
        return CartQuerySet(self.model, using=self._db)

    def with_totals(self):
        return self.get_queryset().with_totals()
    
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
        cart = (
            self.select_related(None)
            .prefetch_related(
                Prefetch(
                    "ordered",
                    queryset=(
                        OrderedProduct.objects
                        .select_related("product")
                        .prefetch_related(
                            Prefetch(
                                "product__images",
                                queryset=ProductImage.objects.only("id", "product_id", "image"),
                                to_attr="prefetched_images",
                            )
                        )
                    ),
                    to_attr="prefetched_items",
                )
            )
            .get(pk=cart.pk)
        )
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

    def _items_qs(self):
        return self.ordered.select_related('product')

    def save(self, *args, **kwargs):
        if not self.order_number or self.order_number.strip() == "":
            date_str = timezone.now().strftime("%Y%m%d")
            unique_code = uuid.uuid4().hex[:6].upper()
            self.order_number = f"{date_str}-{unique_code}"
        super().save(*args, **kwargs)

    @property
    def cart_total_price(self):
        price_per_item = models.Case(
            models.When(price_at_purchase__isnull=False,
                then=models.F('price_at_purchase')),
            default=(
                models.F('product__price') * (1 - Coalesce(models.F('product__discount'), 0) / 100.0)
            ),
            output_field=models.DecimalField(max_digits=10, decimal_places=2),
        )
        row_total = ExpressionWrapper(
            price_per_item * models.F('quantity'),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
        total = (
            self._items_qs()
            .aggregate(
                total=Coalesce(
                    models.Sum(row_total),
                    Value(0),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )['total'] or Decimal('0')
        )
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    

    
    @cached_property
    def cart_total_quantity(self):
        return self._items_qs().aggregate(total=Coalesce(models.Sum('quantity'), 0))['total'] or 0
    
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
    
    class Meta:
        indexes = [
            models.Index(fields=['session_key']),
            models.Index(fields=['is_completed', 'date_completed']),
        ]

class OrderedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='ordered')
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, related_name='ordered')
    quantity = models.IntegerField(default=0, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.product.title if self.product else f"OrderedProduct #{self.pk}"

    @property
    def total_price(self):
        quantity = Decimal(self.quantity or 0)
        if quantity <= 0:
            return Decimal('0.00')
        if self.price_at_purchase is not None:
            return round(self.price_at_purchase * Decimal(self.quantity), 2)
        if self.product and hasattr(self.product, 'full_price') and self.product.full_price is not None:
            return round(Decimal(self.product.full_price) * Decimal(self.quantity),2)
        return Decimal('0.00')
    
    class Meta:
        indexes = [
            models.Index(fields=['cart']),
            models.Index(fields=['product']),
            models.Index(fields=['added_at']),
        ]