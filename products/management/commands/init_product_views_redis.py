
from django.core.management.base import BaseCommand
from products.models import Product
import redis
from django.conf import settings
r = redis.Redis(host=settings.REDIS_HOST,
 port=settings.REDIS_PORT,
 db=settings.REDIS_DB)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        key = 'product:views:zset'
        products = Product.objects.all()
        count = 0
        for product in products:
            if not r.zscore(key, product.id):
                r.zadd(key, {product.id: product.watched or 0})
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Initialized {count} products in Redis'))
