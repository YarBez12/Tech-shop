from django.core.management.base import BaseCommand
from users.models import User
from products.models import FavouriteProduct, Product
import redis
from django.conf import settings

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)


class Command(BaseCommand):
    def handle(self, *args, **options):
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
        self.stdout.write(self.style.SUCCESS("Successfully synced favourite products from Redis into database"))
