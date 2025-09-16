from celery import shared_task
from products.models import Product, FavouriteProduct
import redis
from django.conf import settings
from users.models import User
from conf.utils import r

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

@shared_task
def sync_favourites_to_db():

    for user in User.objects.filter(is_active=True):
        redis_key = f'favourite:user:{user.id}'
        redis_product_ids = r.smembers(redis_key)
        redis_product_ids = {int(pid) for pid in redis_product_ids}
        db_product_ids = set(FavouriteProduct.objects.filter(user=user).values_list('product_id', flat=True))

        for pid in redis_product_ids - db_product_ids:
            if Product.objects.filter(id=pid).exists():
                FavouriteProduct.objects.get_or_create(user=user, product_id=pid)

        for pid in db_product_ids - redis_product_ids:
            FavouriteProduct.objects.filter(user=user, product_id=pid).delete()

    print("Favourite products synchronized.")
