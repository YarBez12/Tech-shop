# signals.py

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from products.models import Product
from django.utils import timezone
from django.conf import settings
from conf.utils import r

@receiver(post_save, sender=Product)
def init_product_views(sender, instance, created, **kwargs):
    if created:
        key = 'product:views:zset'
        if not r.zscore(key, instance.id):
            r.zadd(key, {instance.id: 0})


@receiver(m2m_changed, sender=Product.tags.through)
def product_tags_changed(sender, instance, action, pk_set, reverse, **kwargs):
    if action == "post_add" and pk_set:
        Product.objects.filter(pk=instance.pk).update(updated_at=timezone.now())
    elif action == "post_remove" and pk_set:
        Product.objects.filter(pk=instance.pk).update(updated_at=timezone.now())
    elif action == "post_clear":
        Product.objects.filter(pk=instance.pk).update(updated_at=timezone.now())