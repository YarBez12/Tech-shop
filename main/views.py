from django.shortcuts import render
from products.models import Category, Product
from django.urls import get_resolver
from difflib import get_close_matches
import redis
from django.conf import settings
r = redis.Redis(host=settings.REDIS_HOST,
 port=settings.REDIS_PORT,
 db=settings.REDIS_DB)

def get_top_viewed_products(limit=10, oversample=5):
    return [int(pid) for pid in r.zrevrange('product:views:zset', 0, limit * max(1, oversample) - 1)]



def index(request):
    # parent_categories = Category.objects.filter(parent=None)
    # child_categories = Category.objects.exclude(parent = None)
    # popular_products = Product.objects.order_by('-watched')[:12]
    NEED = 12
    top_product_ids = get_top_viewed_products(limit=NEED, oversample=5)

    if top_product_ids:
        products_dict = {product.id: product for product in Product.objects.filter(id__in=top_product_ids, is_active=True, quantity__gt=0)}
        popular_products_ordered = [products_dict[pid] for pid in top_product_ids if pid in products_dict]
    else:
        popular_products_ordered = []
    if len(popular_products_ordered) < NEED:
        missing = NEED - len(popular_products_ordered)
        fallback_qs = (
            Product.objects
            .filter(is_active=True, quantity__gt=0)
            .exclude(id__in=[p.id for p in popular_products_ordered])
            .order_by('-watched')[:missing]
        )
        popular_products_ordered.extend(fallback_qs)
    # print(popular_products_ordered)
    context = {
        'title': 'Home Page',
        # 'parent_categories': parent_categories,
        # 'child_categories':child_categories,
        'popular_products': popular_products_ordered[:NEED],
    }
    return render(request, 'main/index.html', context)


def custom_404(request, exception):

    return render(request, '404.html', status=404)

def test_404(request):
    return custom_404(request, exception=None)

