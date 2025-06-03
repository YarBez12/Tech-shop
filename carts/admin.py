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
admin.site.register(Receiver)
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'receiver', 'created_at', 'is_completed',
                    'date_completed', 'order_number', order_payment, cart_detail]
    list_filter = ['is_completed']
    actions = [export_to_csv]
# admin.site.register(Cart)
admin.site.register(OrderedProduct)

