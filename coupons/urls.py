from django.urls import path
from .views import *
app_name = 'coupons'

urlpatterns = [
    path('apply/', coupon_apply, name='apply'),
]