from django.contrib import admin
from .models import User, Address, Action

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'email', 'is_staff', 'is_superuser')
    list_display_links = ('pk', 'email')
    list_filter = ('is_staff', 'is_superuser')
    list_editable = ('is_staff', 'is_superuser')
    
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('address_field1', 'city', 'country', 'postal_code')
    list_display_links = ('address_field1', 'postal_code')
    list_filter = ('city', 'country')


admin.site.register(Action)
