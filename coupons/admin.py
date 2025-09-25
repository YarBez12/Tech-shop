from django.contrib import admin
from .models import Coupon, CouponUsage
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'active', 'valid_from', 'valid_to', 'usage_count')
    list_filter = ('active', 'valid_from', 'valid_to')
    search_fields = ('code',)
    date_hierarchy = 'valid_from'
    ordering = ('-valid_from',)
    list_editable = ('discount', 'active')

    def usage_count(self, obj):
        return obj.usages.count()
    usage_count.short_description = 'Usages'

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user', 'used_at')
    list_filter = ('used_at', 'coupon')
    search_fields = ('coupon__code', 'user__email')
    date_hierarchy = 'used_at'
    list_select_related = ('coupon', 'user')