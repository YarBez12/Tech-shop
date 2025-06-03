from django.urls import path
from .views import *
from . import webhooks


app_name = 'carts'


urlpatterns = [
    path('', CartView.as_view(), name = 'cart'),
    path('add/<slug:product_slug>/', add_to_cart, name='add_to_cart'),
    path('remove/<slug:product_slug>/', remove_from_cart, name='remove_from_cart'),
    path('delete_full/<slug:product_slug>/', delete_full_item_from_cart, name = 'delete_full_from_cart'),
    path('reduce_quantity/<slug:ordered_product_pk>/', reduce_quantity, name='reduce_quantity'),
    path('checkout/', CheckoutView.as_view(), name = 'checkout'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('payment-success/', payment_success, name='payment_success'),
    path('payment-cancel/', payment_cancel, name='payment_cancel'),
    path('webhook/', webhooks.stripe_webhook, name='stripe-webhook'),
    path('admin/cart/<int:cart_id>/', admin_cart_detail, name='admin_cart_detail'),
]