from products.models import Product, ProductCharacteristic
from products.utils.filters import sort_with_option, filter_products, filter_categories
from django.db.models import F, ExpressionWrapper, DecimalField, Value, Avg, Prefetch
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.generic import ListView
from products.utils.mixins import EndlessPaginationMixin
from products.utils.filters import get_prefetched_characteristics_query, get_prefetched_images_query




class SearchResults(EndlessPaginationMixin, ListView):
    model = Product
    template_name = 'products/search_results.html'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        session_key = "ui_state:search_results"
        ui_state = self.request.session.get(session_key, {})
        sort_option = ui_state.get('sort', 'title')
        search_query = self.request.GET.get('q', '').strip()
        products = filter_products(search_query)
        products = sort_with_option(sort_option, products) if sort_option else products
        return (products.select_related('brand','category','user')
                    .prefetch_related('tags', get_prefetched_characteristics_query(), get_prefetched_images_query()))

    def get_template_names(self):
        if self.request.GET.get('products_only'):
            return ['products/components/_product_endless_list.html']  
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q', '').strip()
        categories = filter_categories(search_query).annotate(
            price=Avg(
                ExpressionWrapper(
                F('products__price') * (Value(100) - Coalesce(F('products__discount'), Value(0))) / Value(100),
                output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
        )
        session_key = "ui_state:search_results"
        ui_state = self.request.session.get(session_key, {})
        context['saved_ui_state'] = ui_state
        sort_option = ui_state.get('sort', 'title')
        if sort_option:
            categories = sort_with_option(sort_option, categories)
        context['categories'] = categories
        context['title'] = 'Search results'
        context['is_search'] = True
        return context
    
   

def search_suggestions(request):
    search_query = request.GET.get('q', '').strip()
    if not search_query:
        return JsonResponse({'categories': [], 'products': []})
    categories = filter_categories(search_query)
    if len(categories) >= 10:
        return JsonResponse({
        'categories': [
            {
                'title': category.title,
                'url': category.get_absolute_url(),
            } for category in categories[:10]
        ],
        'products': [] 
    })
    else:
        products = filter_products(search_query)
        return JsonResponse({
            'categories': [
            {
                'title': category.title,
                'url': category.get_absolute_url(),
            } for category in categories
            ],
            'products': [
            {
                'title': product.title,
                'url': product.get_absolute_url(),
            } for product in products[:(10-len(categories))]
            ] 
        })