# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from products.models import Product
import redis
from django.conf import settings
from conf.utils import r

@receiver(post_save, sender=Product)
def init_product_views(sender, instance, created, **kwargs):
    if created:
        key = 'product:views:zset'
        if not r.zscore(key, instance.id):
            r.zadd(key, {instance.id: 0})