from django.contrib import admin
from .models import *
import csv
import datetime
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.urls import reverse

def cart_detail(obj):
    url = reverse('carts:admin_cart_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')

class OrderedProductInline(admin.TabularInline):
    model = OrderedProduct
    extra = 0
    autocomplete_fields = ('product',)
    fields = ('product', 'quantity', 'price_at_purchase', 'row_total')
    readonly_fields = ('row_total',)

    def row_total(self, obj):
        return obj.total_price
    row_total.short_description = 'Row total'


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = f'attachment; filename={opts.verbose_name}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not \
              field.many_to_many and not field.one_to_many]
    writer.writerow([field.verbose_name for field in fields])
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response
export_to_csv.short_description = 'Export to CSV'


def order_payment(obj):
    url = obj.get_stripe_url()
    if obj.stripe_id:
        html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
        return mark_safe(html)
    return ''
order_payment.short_description = 'Stripe payment'

@admin.register(Receiver)
class ReceiverAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'email', 'phone',
        'user', 'address_inline',
    )
    list_display_links = ('first_name', 'last_name')
    list_filter = (
        'user',
        'address__country', 'address__city', 'address__state',
    )
    search_fields = (
        'first_name', 'last_name', 'email', 'phone',
        'user__email', 'user__username',
        'address__address_field1', 'address__city', 'address__postal_code',
    )
    list_select_related = ('user', 'address')
    autocomplete_fields = ('user', 'address')

    def address_inline(self, obj):
        if not obj.address:
            return '—'
        a = obj.address
        parts = [a.address_field1]
        if a.address_field2:
            parts.append(a.address_field2)
        if a.city:
            parts.append(a.city)
        if a.state:
            parts.append(a.state)
        if a.country:
            parts.append(a.country)
        if a.postal_code:
            parts.append(a.postal_code)
        return ', '.join(filter(None, parts))
    address_inline.short_description = 'Address'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_number', 'created_at', 'is_completed',
                'date_completed', 'receiver', 'coupon', 'discount',
                'items_qty', 'total_before', 'total_after',
                order_payment, cart_detail]
    list_display_links = ('id', 'order_number')
    list_editable = ('is_completed', 'discount')
    search_fields = ('order_number', 'receiver__first_name', 'receiver__last_name',
                     'receiver__email', 'stripe_id')
    list_filter = ['is_completed', 'created_at', 'date_completed', 'coupon']
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_select_related = ('receiver', 'coupon')
    actions = [export_to_csv]
    inlines = (OrderedProductInline,)
    readonly_fields=('discount',)

    def items_qty(self, obj):
        return obj.cart_total_quantity
    items_qty.short_description = 'Qty'

    def total_before(self, obj):
        return obj.cart_total_price
    total_before.short_description = 'Total (before)'

    def total_after(self, obj):
        return obj.cart_total_price_after_discount
    total_after.short_description = 'Total (after)'


@admin.register(OrderedProduct)
class OrderedProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'cart', 'product', 'quantity',
        'price_at_purchase', 'row_total', 'added_at',
    )
    list_editable = ('quantity', 'price_at_purchase')
    list_display_links = ('id',)
    list_filter = ('added_at', 'cart__is_completed', 'product')
    search_fields = (
        'cart__order_number', 'product__title',
        'cart__receiver__first_name', 'cart__receiver__last_name',
        'cart__receiver__email',
    )
    list_select_related = ('product', 'cart', 'cart__receiver')
    autocomplete_fields = ('product', 'cart')
    readonly_fields = ('row_total',)

    def row_total(self, obj):
        return obj.total_price
    row_total.short_description = 'Row total'
