from django import template
from django.db.models import OuterRef, Subquery
from products.models import Subcription
from django.db.models import Count, Q
from conf.utils import r
from products.models import Category, Product, ProductCharacteristic, Brand
from django.conf import settings
from products.utils.redis_utils import get_category_views
from django.core.cache import cache


register = template.Library()

@register.simple_tag()
def child_categories(parent_category, count):
    count = int(count)
    cache_key = f"main:child_categories:{parent_category.id}:{count}"
    categories = cache.get(cache_key)
    if categories is not None:
        return categories

    categories_qs = (Category.objects
          .filter(parent=parent_category)
          .annotate(
              product_count=Count(
                  "products",
                  filter=Q(products__is_active=True, products__quantity__gt=0),
                  distinct=True,
              )
          )
          .filter(product_count__gt=0)
          .only('id', 'slug', 'title', 'image', 'parent_id'))

    categories = list(categories_qs)
    categories.sort(key=lambda c: get_category_views(c.id), reverse=True)

    categories = categories[:count]
    cache.set(cache_key, categories, 300)
    return categories

@register.simple_tag()
def parent_categories():
    cache_key = "main:parent_categories"
    categories = cache.get(cache_key)
    if categories is not None:
        return categories
    
    categories_qs = (Category.objects
          .filter(parent=None)
          .annotate(
              child_products=Count(
                  "children__products",
                  filter=Q(children__products__is_active=True,
                           children__products__quantity__gt=0),
                  distinct=True,
              )
          )
          .filter(child_products__gt=0)
          .only('id', 'slug', 'title', 'image'))
    categories = list(categories_qs)
    cache.set(cache_key, categories, 300)  
    return categories

@register.simple_tag()
def brands(count = 15):
    cache_key = "main:brands"
    brands_list = cache.get(cache_key)
    if brands_list is not None:
        return brands_list
    brands_qs = (
        Brand.objects
        .annotate(
            product_count=Count(
                'products',
                filter=Q(products__is_active=True, products__quantity__gt=0),
                distinct=True,
            )
        )
        .filter(product_count__gt=0)
        .only('id', 'slug', 'name', 'image', 'foundation_year', 'description')
        .order_by('-product_count')[:count]
    )
    brands_list = list(brands_qs)
    cache.set(cache_key, brands_list, 300)
    return brands_list

@register.simple_tag()
def product_number_by_page(parent_count, count):
    return int(parent_count)*4 + int(count)

@register.filter()
def get_grade_range(grade):
    return list(range(grade))

    
@register.filter()
def get_product_characteristics(characteristic):
    subquery = ProductCharacteristic.objects.filter(
        characteristic=characteristic,
        value=OuterRef('value')  
    ).order_by('id').values('id')[:1]  

    return ProductCharacteristic.objects.filter(
        id__in=Subquery(subquery)
    )




@register.simple_tag()
def favourite_products(request):
    if not request.user.is_authenticated:
        return []
    ids = [int(pid) for pid in r.smembers(f"favourite:user:{request.user.id}")]
    qs = (Product.objects
          .filter(pk__in=ids, is_active=True, quantity__gt=0)
          .select_related('brand', 'category', 'user')
          .prefetch_related('images', 'tags'))
    return list(qs)
@register.simple_tag()
def favourite_ids(user):
    if not user.is_authenticated:
        return []
    return [int(pid) for pid in r.smembers(f"favourite:user:{user.id}")]


@register.filter()
def display_tags(tags, query):
    matching = []
    if  query:
        query_lower = query.lower()
        terms = query_lower.split()
        for term in terms:
            matching += [tag for tag in tags if term in tag.name.lower() and tag not in matching]
    non_matching = [tag for tag in tags if tag.display and tag not in matching]
    result = []
    for tag in matching:
        result.append({
            'text': f"<strong>{tag.name}</strong>"
        })
    for tag in non_matching:
        result.append({
            'text': tag.name
        })
    return result

@register.filter
def is_subscribed(brand, user):
    if not getattr(user, "is_authenticated", False):
        return False
    return Subcription.objects.filter(brand=brand, user=user).exists()
