from django.shortcuts import render
from products.models import Product
from .utils import get_top_viewed_products
from django.core.cache import cache
from django.db.models import Prefetch




def index(request):
    NEED = 12

    cache_key = "main:index:popular_products"
    cached = cache.get(cache_key)
    if cached is not None:
        return render(request, 'main/index.html', {'title': 'Home Page', 'popular_products': cached})

    top_product_ids = get_top_viewed_products(limit=NEED, oversample=5)
    base_qs = (Product.objects
        .select_related('brand', 'category')
        .prefetch_related(
            'tags',
            Prefetch('images')
        )
        .only(
            'id', 'title', 'slug', 'price', 'discount', 'quantity', 'is_active',
            'brand__name', 'category__title'
        )
        .filter(is_active=True, quantity__gt=0)
    )
    popular_products_ordered = []
    if top_product_ids:
        products = base_qs.filter(id__in=top_product_ids)
        products_dict = {product.id: product for product in products}
        popular_products_ordered = [products_dict[pid] for pid in top_product_ids if pid in products_dict]
    if len(popular_products_ordered) < NEED:
        missing = NEED - len(popular_products_ordered)
        fallback_qs = (
            base_qs.exclude(id__in=[p.id for p in popular_products_ordered])
                   .order_by('-watched')[:missing]
        )
        popular_products_ordered.extend(fallback_qs)
    popular_products_ordered = popular_products_ordered[:NEED]
    cache.set(cache_key, popular_products_ordered, 60)
    return render(request, 'main/index.html', {
        'title': 'Home Page',
        'popular_products': popular_products_ordered[:NEED],
    })


def custom_404(request, exception):

    return render(request, '404.html', status=404)

def test_404(request):
    return custom_404(request, exception=None)

