from django.core.management.base import BaseCommand
from products.models import FavouriteProduct
from users.models import User
import redis
from django.conf import settings

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for user in User.objects.filter(is_active=True):
            fav_ids = FavouriteProduct.objects.filter(user=user).values_list('product_id', flat=True)
            for pid in fav_ids:
                r.sadd(f'favourite:user:{user.id}', pid)
        self.stdout.write(self.style.SUCCESS('Favourites successfully synced to Redis.'))
