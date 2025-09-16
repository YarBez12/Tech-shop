from django.core.management.base import BaseCommand
from products.models import Product
import redis
from django.conf import settings
from conf.utils import r


class Command(BaseCommand):
    help = 'Saves all products views from Redis to database'

    def handle(self, *args, **kwargs):
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
        self.stdout.write(self.style.SUCCESS(f'Synchronized {updated} products.'))

