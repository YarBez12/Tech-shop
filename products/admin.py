from django.contrib import admin
from django import forms
from .models import *
from taggit.models import Tag
from django.db import transaction
from django.utils.html import escape
from users.tasks import send_email_task

class ProductCharacteristicInline(admin.TabularInline):
    model = ProductCharacteristic
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if obj and obj.category:
            formset.form.base_fields['characteristic'].queryset = obj.category.characteristics.all()
        else:
            formset.form.base_fields['characteristic'].queryset = Characteristic.objects.none()

        return formset


@admin.register(ProductActivationRequest)
class ProductActivationRequestAdmin(admin.ModelAdmin):
    list_display = ('product','user','status','created')
    list_filter = ('status','created')
    search_fields = ('product__title','user__email')
    list_select_related = ('product', 'user')
    date_hierarchy = 'created'

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not (change and "status" in form.changed_data):
            return

        p = obj.product
        owner = getattr(p, "user", None)
        owner_email = getattr(owner, "email", None)

        try:
            product_url = request.build_absolute_uri(p.get_absolute_url())
        except Exception:
            product_url = p.get_absolute_url()

        if obj.status == ProductActivationRequest.Status.APPROVED:
            if p.quantity <= 0:
                p.quantity = 1
            p.is_active = True
            p.save(update_fields=["is_active", "quantity"])

            if owner_email:
                subject = "Your product has been approved ✅"
                text = (
                    f"Hi!\n\nYour product \"{p.title}\" has been approved and is now visible in the catalog.\n"
                    f"Link: {product_url}\n\nHave a great day!"
                )
                html = (
                    f"<p>Hi!</p>"
                    f"<p>Your product <strong>{escape(p.title)}</strong> has been approved and is now visible in the catalog.</p>"
                    f"<p><a href='{product_url}'>Open product</a></p>"
                    f"<p>Have a great day!</p>"
                )
                send_email_task.delay(subject, text, html, owner_email)

        elif obj.status == ProductActivationRequest.Status.REJECTED:
            if owner_email:
                subject = "Your product was not approved ❌"
                text = (
                    f"Hi!\n\nUnfortunately, your product \"{p.title}\" was not approved and has been removed."
                )
                html = (
                    f"<p>Hi!</p>"
                    f"<p>Unfortunately, your product <strong>{escape(p.title)}</strong> was not approved and has been removed.</p>"
                )
                send_email_task.delay(subject, text, html, owner_email)
            p.delete()


class ImageInline(admin.TabularInline):
    extra = 1

class ProductImageInline(ImageInline):
    model = ProductImage
    fk_name = 'product'

class ReviewImageInline(ImageInline):
    model = ReviewImage
    fk_name = 'review'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = (ProductCharacteristicInline, ProductImageInline)
    list_display = ('pk', 'title', 'price', 'quantity', 'watched', 'updated_at', 'warranty', 'category', 'brand', 'is_active')
    list_display_links = ('pk', 'title')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'category', 'brand', 'created_at')
    search_fields = ('title', 'summary', 'sku')
    readonly_fields = ('watched', 'created_at', 'updated_at')
    prepopulated_fields = {'slug' : ('title', )}
    autocomplete_fields = ('category', 'brand')
    list_select_related = ('category', 'brand')
    date_hierarchy = 'created_at'
    class Media:
        js = ('../static/js/product_admins.js',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'parent')
    list_display_links = ('pk', 'title')
    list_filter = ('parent', )
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug' : ('title', )}
    autocomplete_fields = ('parent',)





@admin.register(CustomTag)
class CustomTagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'display')
    list_editable = ('display',)
    list_display_links = ('pk', 'name')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'foundation_year')
    list_display_links = ('pk', 'name')
    list_filter = ('foundation_year', )
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug' : ('name', )}

@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'category', 'main')
    list_display_links = ('pk', 'title')
    list_filter = ('category', 'main')
    search_fields = ('title', 'slug', 'category__title')
    prepopulated_fields = {'slug' : ('title', )}
    list_editable = ('main',)
    autocomplete_fields = ('category',)

@admin.register(ProductCharacteristic)
class ProductCharacteristicAdmin(admin.ModelAdmin):
    list_display = ('product', 'characteristic', 'value')
    list_filter = ('product', 'characteristic')
    search_fields = ('product__title', 'characteristic__title', 'value')
    autocomplete_fields = ('product', 'characteristic')
    list_select_related = ('product', 'characteristic')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    inlines = (ReviewImageInline, )
    list_display = ('pk', 'title', 'created_at', 'grade', 'product', 'user')
    list_display_links = ('pk', 'title')
    list_filter = ('created_at', 'grade', 'product', 'user')
    search_fields = ('title', 'product__title', 'user__email')
    readonly_fields = ('title', 'summary', 'pros', 'cons', 'created_at', 'grade', 'product')
    list_select_related = ('product', 'user')
    date_hierarchy = 'created_at'

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', )
    list_filter = ('product', )
    search_fields = ('product__title',)
    autocomplete_fields = ('product',)
    list_select_related = ('product',)

@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ('review', )
    list_filter = ('review', )
    search_fields = ('review__title', 'review__product__title')
    autocomplete_fields = ('review',)
    list_select_related = ('review',)

@admin.register(Subcription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'brand', 'created')
    list_filter = ('user', 'brand')
    search_fields = ('user__email', 'brand__name')
    autocomplete_fields = ('user', 'brand')
    list_select_related = ('user', 'brand')
    date_hierarchy = 'created'


@admin.register(FavouriteProduct)
class FavouriteProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    list_filter = ('user', 'product')
    search_fields = ('user__email', 'product__title')
    autocomplete_fields = ('user', 'product')
    list_select_related = ('user', 'product')