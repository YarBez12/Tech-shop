import math
import re
from django import template
from django.db.models import Sum
from django.utils.http import urlencode
from django.db.models import OuterRef, Subquery
from products.models import FavouriteProduct
from django.utils.safestring import mark_safe



from products.models import Category, Product, Characteristic, ProductCharacteristic

register = template.Library()

@register.simple_tag()
def child_categories(parent_category, count):
    return Category.objects.filter(parent=parent_category).annotate(
        total_watched = Sum('products__watched')
    ).order_by('-total_watched')[:int(count)]

@register.simple_tag()
def parent_categories():
    return Category.objects.filter(parent=None)

@register.simple_tag()
def product_number_by_page(parent_count, count):
    return int(parent_count)*4 + int(count)

@register.filter()
def get_item(queryset, index):
    return queryset[int(index)]

@register.simple_tag()
def get_top_subcategory_products(subcategory):
    return Product.objects.filter(category=subcategory).order_by('watched')[:6]

@register.filter()
def get_grade_range(grade):
    return list(range(grade))

@register.filter
def floor_int(value):
    try:
        return math.floor(float(value))
    except (ValueError, TypeError):
        return value
    
@register.filter
def ceil_int(value):
    try:
        return math.ceil(float(value))
    except (ValueError, TypeError):
        return value
    
@register.filter()
def get_product_characteristics(characteristic):
    subquery = ProductCharacteristic.objects.filter(
        characteristic=characteristic,
        value=OuterRef('value')  
    ).order_by('id').values('id')[:1]  

    return ProductCharacteristic.objects.filter(
        id__in=Subquery(subquery)
    )
@register.filter
def get_item_from_dict(dictionary, key):
    return dictionary.get(key, [])

@register.simple_tag(takes_context=True)
def change_params(context, **kwargs):
    query = context['request'].GET.copy()  
    for key, value in kwargs.items():
        query.setlist(key, value if isinstance(value, list) else [value]) 
    return urlencode(query, doseq=True) 

@register.simple_tag()
def favourite_products(request):
    if request.user.is_authenticated:
        fav_products = FavouriteProduct.objects.filter(user=request.user)
        return [f.product for f in fav_products]
    return []

@register.filter()
def highlight(text, query):
    if not text:
        return ""
    if  query:
        terms = query.split()
        pattern = re.compile("|".join(re.escape(term) for term in terms), re.IGNORECASE)
        def replacer(match):
            return f"<strong>{match.group(0)}</strong>"
        highlighted_text = pattern.sub(replacer, text)
        return mark_safe(highlighted_text)
    return text

@register.filter()
def display_tags(tags, query):
    matching = []
    if  query:
        query_lower = query.lower()
        terms = query_lower.split()
        for term in terms:
            matching += [tag for tag in tags if term in tag.tag.lower() and tag not in matching]
    non_matching = [tag for tag in tags if tag.display and tag not in matching]
    result = []
    for tag in matching:
        result.append({
            'text': f"<strong>{tag.tag}</strong>"
        })
    for tag in non_matching:
        result.append({
            'text': tag.tag
        })
    return result