from products.models import Category, Product
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import F, ExpressionWrapper, DecimalField, Value
from django.db.models.functions import Coalesce, Lower


def filter_products(search_query):
    products = Product.objects.filter(is_active=True)
    if search_query:
        vector = SearchVector('title', weight='A') + \
             SearchVector('description', weight='B') + \
             SearchVector('tags__name', weight='C') + \
             SearchVector('sku', weight='A')

        query = SearchQuery(search_query)


        qs = Product.objects.annotate(
            rank=SearchRank(vector, query)
        ).filter(rank__gte=0.1).order_by('-rank')

        product_ids = qs.values('id').distinct()
        products = Product.objects.filter(id__in=product_ids, is_active=True)
    return products

def filter_categories(search_query):
    categories = Category.objects.all()
    if search_query:
        vector = SearchVector('title', weight='A')
        query = SearchQuery(search_query)
        categories = Category.objects.annotate(
            rank=SearchRank(vector, query)
        ).filter(rank__gte=0.1).distinct().order_by(F('parent').asc(nulls_first=True), '-rank')
    categories = categories.order_by(F('parent').asc(nulls_first=True))
    return categories

def sort_with_option(sort_option, items):
    model = items.model
    if sort_option in ['price', '-price']:
        model_fields = [f.name for f in model._meta.get_fields()]
        if 'price' in model_fields and 'discount' in model_fields:
            items = items.annotate(
                calculated_full_price=ExpressionWrapper(
                    F('price') * (Value(100) - Coalesce(F('discount'), Value(0))) / Value(100),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
            if sort_option == 'price':
                items = items.order_by('calculated_full_price')
            else:
                items = items.order_by('-calculated_full_price')
        else:
            items = items.order_by(sort_option)
    elif sort_option == 'title':
        items = items.annotate(lower_title=Lower('title')).order_by('lower_title')
    elif sort_option == '-title':
        items = items.annotate(lower_title=Lower('title')).order_by('-lower_title')
    else:
        items = items.order_by(sort_option)
    return items

