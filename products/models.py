from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from decimal import Decimal
from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase
from django.utils.text import slugify
from django.utils import timezone
from users.models import User



class Category(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null = True)
    parent = models.ForeignKey('self', 
                               on_delete=models.SET_NULL, 
                               null=True, blank=True,
                               related_name='children')
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        if self.parent:
            return reverse('products:subcategory_detail', kwargs={'category_slug': self.parent.slug, 
                                                                  'subcategory_slug': self.slug})
        return reverse('products:category_detail', kwargs={'category_slug': self.slug})
    
    class Meta:
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=['slug']),
        ]
    

class CustomTag(TagBase):
    display = models.BooleanField(default=True)

class CustomTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(
        CustomTag,
        on_delete=models.CASCADE,
        related_name="tagged_items"
    )
class Brand(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='brands/', null=True, blank=True)
    foundation_year = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:brand_details", kwargs={"slug": self.slug})
    
    class Meta:
        indexes = [
            models.Index(fields=['slug']),
        ]


class Characteristic(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=150, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='characteristics')
    main = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class Product(models.Model):
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    summary = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True) 
    price = models.FloatField(default=9.99)
    discount = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    quantity = models.IntegerField()
    watched = models.IntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now)
    warranty = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True)
    tags = TaggableManager(through=CustomTaggedItem, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    is_active = models.BooleanField(default=True)
    sku = models.CharField(max_length=50, unique=True, blank=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='products')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.sku:
            self.sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        tracked_fields = ("title", "price", "discount", "brand_id", "category_id")
        if self.pk:
            try:
                old = Product.objects.only(*tracked_fields).get(pk=self.pk)
            except Product.DoesNotExist:
                old = None
            if old:
                if any(
                    getattr(old, field) != getattr(self, field)
                    for field in tracked_fields
                ):
                    print(444)
                    self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:product_detail", kwargs={"product_slug": self.slug})
    

    def __str__(self):
        return self.title
    
    @property
    def full_price(self):
        if self.discount:
            return round(Decimal(self.price) * (Decimal(100) - Decimal(self.discount)) / Decimal(100), 2)
        return self.price
    
    @property
    def first_photo(self):
        first_image = self.images.first()
        return first_image.image.url if first_image else None
    
    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'quantity']),
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['category', 'is_active']),
        ]
        ordering = ['-created_at']


class ProductActivationRequest(models.Model):
    class Status(models.TextChoices):
        PENDING  = 'pending',  'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='activation_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activation_requests')
    status = models.CharField(max_length=10, choices=Status.choices, default='pending')
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.product} — {self.user} — {self.status}"
    
class ProductCharacteristic(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_characteristics')
    characteristic = models.ForeignKey(Characteristic, on_delete=models.CASCADE, related_name='product_characteristics')
    value = models.CharField(max_length=200)


    def __str__(self):
        return f"{self.characteristic.title}: {self.value}"
    
    class Meta:
        unique_together = ('product', 'characteristic')  

class Review(models.Model):
    title = models.CharField(max_length=300)
    summary = models.TextField(null=True, blank=True)
    pros = models.TextField(null=True, blank=True)
    cons = models.TextField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    grade = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')

    def __str__(self):
        return self.title
    
    def delete_review(self):
        return reverse('products:review_delete', kwargs={'pk': self.pk})
    
    def edit_review(self):
        return reverse('products:review_edit', kwargs={'pk': self.pk})
    
    def get_absolute_url(self):
        return reverse("products:product_detail", kwargs={"product_slug": self.product.slug})
    
    class Meta:
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['created_at']),
        ]

class ProductImage(models.Model):
    image = models.ImageField(upload_to='products/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    class Meta:
        indexes = [models.Index(fields=['product'])]

class ReviewImage(models.Model):
    image = models.ImageField(upload_to='reviews/')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    class Meta:
        indexes = [models.Index(fields=['review'])]


class FavouriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourite_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favourite_products')

    def __str__(self):
        return self.product.title
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['product']),
        ]
    
class Subcription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subcriptions')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='subscribers')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'brand')  
        indexes = [
            models.Index(fields=['user', 'brand']),
        ]

    def __str__(self):
        return f"{self.user} subscribed on {self.brand}"