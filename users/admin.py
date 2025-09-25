from django.contrib import admin
from .models import User, Address, Action, NotificationState


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'email', 'first_name', 'last_name', 'phone', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined')
    list_display_links = ('pk', 'email')
    list_editable = ('is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    autocomplete_fields = ('address',)
    list_select_related = ('address',)
    date_hierarchy = 'date_joined'
    ordering = ('-date_joined',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('pk', 'address_field1', 'city', 'state', 'country', 'postal_code')
    list_display_links = ('pk', 'address_field1')
    list_filter = ('country', 'city', 'state')
    search_fields = ('address_field1', 'address_field2', 'city', 'state', 'country', 'postal_code')
    ordering = ('country', 'city', 'address_field1')


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'verb', 'created', 'target_repr')
    list_display_links = ('pk', 'user')
    list_filter = ('verb', 'created')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'verb', 'target_id')
    autocomplete_fields = ('user',)
    list_select_related = ('user',)
    date_hierarchy = 'created'
    ordering = ('-created',)

    def target_repr(self, obj):
        return f'{obj.target_ct}#{obj.target_id}'
    target_repr.short_description = 'Target'


@admin.register(NotificationState)
class NotificationStateAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'last_seen_news', 'last_seen_actions')
    list_display_links = ('pk', 'user')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    list_filter = ('last_seen_news', 'last_seen_actions')
    autocomplete_fields = ('user',)
    list_select_related = ('user',)
    date_hierarchy = 'last_seen_news'
