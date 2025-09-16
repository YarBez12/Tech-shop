from django import template
from django.db.models import OuterRef, Subquery
from products.models import Subcription
from django.db.models import Count, Q
from conf.utils import r
from products.models import Category, Product, ProductCharacteristic, Brand
from django.conf import settings
from products.utils.redis_utils import get_category_views

register = template.Library()

@register.simple_tag()
def child_categories(parent_category, count):
    categories = (
        Category.objects
        .filter(parent=parent_category)
        .annotate(
            product_count=Count(
                "products",
                filter=Q(products__is_active=True, products__quantity__gt=0),
                distinct=True,
            )
        )
        .filter(product_count__gt=0)
    )

    categories = sorted(
        categories,
        key=lambda c: get_category_views(c.id),
        reverse=True
    )
    return categories[:int(count)]

@register.simple_tag()
def parent_categories():
    return (
        Category.objects
        .filter(parent=None)
        .annotate(
            child_products=Count(
                "children__products",
                filter=Q(children__products__is_active=True, children__products__quantity__gt=0),
                distinct=True,
            )
        )
        .filter(child_products__gt=0)
    )

@register.simple_tag()
def brands(count = 15):
    return (
        Brand.objects
        .annotate(
            product_count=Count(
                'products',
                filter=Q(products__is_active=True, products__quantity__gt=0),
                distinct=True,
            )
        )
        .filter(product_count__gt=0)
        .order_by('-product_count')[:count]
    )

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
    if request.user.is_authenticated:
        redis_ids = r.smembers(f"favourite:user:{request.user.id}")
        product_ids = [int(pid) for pid in redis_ids]
        return Product.objects.filter(pk__in=product_ids, is_active=True)
    return []


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
    return Subcription.objects.filter(brand=brand, user=user).exists()
