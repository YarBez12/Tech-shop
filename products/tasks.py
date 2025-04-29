from celery import shared_task
from products.models import Product
import redis
from django.conf import settings

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

@shared_task
def sync_views_from_redis():
    key = 'product:views:zset'
    all_views = r.zrange(key, 0, -1, withscores=True)
    updated = 0
    for pid, views in all_views:
        try:
            product_id = int(pid)
            views_count = int(views)
            product = Product.objects.get(id=product_id)
            product.watched = views_count
            product.save(update_fields=['watched'])
            updated += 1
        except Product.DoesNotExist:
            continue
    return f'Synchronized {updated} products.'
