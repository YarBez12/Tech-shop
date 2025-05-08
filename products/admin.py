from django.contrib import admin
from django import forms
from .models import *
from taggit.models import Tag

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
    list_filter = ('category', 'brand')
    readonly_fields = ('watched', 'created_at', 'updated_at')
    prepopulated_fields = {'slug' : ('title', )}
    class Media:
        js = ('../static/js/product_admins.js',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'parent')
    list_display_links = ('pk', 'title')
    list_filter = ('parent', )
    prepopulated_fields = {'slug' : ('title', )}

# @admin.register(Tag)
# class TagAdmin(admin.ModelAdmin):
#     list_display = ('pk', 'tag', 'display')
#     list_editable = ('display',)
#     list_display_links = ('pk', 'tag')



@admin.register(CustomTag)
class CustomTagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'display')
    list_editable = ('display',)
    list_display_links = ('pk', 'name')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'foundation_year')
    list_display_links = ('pk', 'name')
    list_filter = ('foundation_year', )
    prepopulated_fields = {'slug' : ('name', )}

@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'category', 'main')
    list_display_links = ('pk', 'title')
    list_filter = ('category', )
    prepopulated_fields = {'slug' : ('title', )}
    list_editable = ('main',)

@admin.register(ProductCharacteristic)
class ProductCharacteristicAdmin(admin.ModelAdmin):
    list_display = ('product', 'characteristic', 'value')
    list_filter = ('product', 'characteristic')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    inlines = (ReviewImageInline, )
    list_display = ('pk', 'title', 'created_at', 'grade', 'product', 'user')
    list_display_links = ('pk', 'title')
    list_filter = ('created_at', 'grade', 'product', 'user')
    readonly_fields = ('title', 'summary', 'pros', 'cons', 'created_at', 'grade', 'product')

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', )
    list_filter = ('product', )

@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ('review', )
    list_filter = ('review', )

@admin.register(Subcription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'brand', 'created')
    list_filter = ('user', 'brand')


@admin.register(FavouriteProduct)
class FavouriteProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    list_filter = ('user', 'product')