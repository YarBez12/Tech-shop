from django.shortcuts import render
from products.models import Category, Product
from django.urls import get_resolver
from difflib import get_close_matches
import redis
from django.conf import settings
r = redis.Redis(host=settings.REDIS_HOST,
 port=settings.REDIS_PORT,
 db=settings.REDIS_DB)

def get_top_viewed_products(limit=10):
    return [int(pid) for pid in r.zrevrange('product:views:zset', 0, limit - 1)]



def index(request):
    # parent_categories = Category.objects.filter(parent=None)
    # child_categories = Category.objects.exclude(parent = None)
    # popular_products = Product.objects.order_by('-watched')[:12]
    top_product_ids = get_top_viewed_products(limit=12)

    if top_product_ids:
        products_dict = {product.id: product for product in Product.objects.filter(id__in=top_product_ids, is_active=True)}
        popular_products_ordered = [products_dict[pid] for pid in top_product_ids if pid in products_dict]
    else:
        popular_products_ordered = []
    # print(popular_products_ordered)
    context = {
        'title': 'Home Page',
        # 'parent_categories': parent_categories,
        # 'child_categories':child_categories,
        'popular_products': popular_products_ordered,
    }
    return render(request, 'main/index.html', context)


def custom_404(request, exception):

    return render(request, '404.html', status=404)

def test_404(request):
    return custom_404(request, exception=None)

