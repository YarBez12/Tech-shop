from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from users.models import Address, User
from products.models import Product
import uuid
from django.utils import timezone

class Receiver(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone = PhoneNumberField(blank=True, null=True)
    email = models.EmailField()
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='receiver')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if self.user:
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

class Cart(models.Model):
    receiver = models.ForeignKey(Receiver, on_delete=models.SET_NULL, blank=True, null=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    date_completed = models.DateField(null=True, blank=True)
    order_number = models.CharField(max_length=20, unique=True, blank=True)



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
        return total_price

    @property
    def cart_total_quantity(self):
        order_products = self.ordered.all()
        total_quantity = sum([product.quantity for product in order_products])
        return total_quantity
    
    def __str__(self):
        if self.receiver:
            return self.receiver.first_name
        return str(self.session_key)

class OrderedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='ordered')
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, related_name='ordered')
    quantity = models.IntegerField(default=0, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.title
    
    @property
    def total_price(self):
        return self.product.price * self.quantity