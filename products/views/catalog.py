from products.models import Product, Brand, Category, CustomTag, Characteristic, Subcription, ProductCharacteristic
from products.utils.filters import sort_with_option
from django.http import HttpResponse
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.db.models import F, ExpressionWrapper, DecimalField, Value, Count, Min, Max, Q, Prefetch
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.generic import DetailView, ListView
from django.shortcuts import resolve_url
from django.utils.http import urlencode
from django.conf import settings
from products.utils.mixins import EndlessPaginationMixin
from products.utils.filters import get_prefetched_characteristics_query, get_prefetched_images_query




class BrandDetails(EndlessPaginationMixin, ListView):
    model = Product
    template_name = 'products/brand.html'
    context_object_name = 'products'
    paginate_by = 8

    def dispatch(self, request, *args, **kwargs):
        self.brand = Brand.objects.only('id', 'name', 'slug').get(slug=self.kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        session_key = f"ui_state:brand:{self.brand.slug}"
        ui_state = self.request.session.get(session_key, {})
        sort_option = ui_state.get('sort', 'title')
        products = Product.objects.filter(
            brand=self.brand,
            is_active=True,
            quantity__gt=0
        ).select_related('brand', 'category', 'user').prefetch_related('images','tags', get_prefetched_characteristics_query(), get_prefetched_images_query())
        return sort_with_option(sort_option, products) if sort_option else products

    def get_template_names(self):
        if self.request.GET.get('products_only'):
            return ['products/components/_product_endless_list.html']  
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.brand.name
        context['brand'] = self.brand
        context['is_brand'] = True
        session_key = f"ui_state:brand:{self.brand.slug}"
        ui_state = self.request.session.get(session_key, {})
        context['saved_ui_state'] = ui_state
        return context


class CategoryDetailView(ListView):
    model = Category
    context_object_name = 'subcategories'
    template_name = 'products/category.html'

    def dispatch(self, request, *args, **kwargs):
        self.parent_category = Category.objects.only('id','title','slug').get(slug=self.kwargs['category_slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        subcategories = (
            Category.objects.filter(parent=self.parent_category)
            .annotate(
                active_products=Count(
                    'products',
                    filter=Q(products__is_active=True, products__quantity__gt=0)
                )
            )
            .filter(active_products__gt=0)
            .only('id','slug','title','image','parent_id')
            .prefetch_related(Prefetch(
                'products',
                queryset=Product.objects.prefetch_related(get_prefetched_images_query()).only('id','category_id','price','discount')
                                        .order_by('-created_at'),
                to_attr='prefetched_products'
            ))
        )

        return subcategories
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.parent_category.title
        return context
    

class SubcategoryDetailView(EndlessPaginationMixin, ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'products/subcategory.html'
    paginate_by = 8



    def get_queryset(self):
        subcategory = Category.objects.get(slug=self.kwargs['subcategory_slug'])
        session_key = f"ui_state:subcategory:{subcategory.slug}"
        ui_state = self.request.session.get(session_key, {})
        sort_option = ui_state.get('sort', 'title')
        filters = {k: v for k, v in ui_state.items() if k != 'sort'}
        products = Product.objects.filter(category=subcategory, is_active=True, quantity__gt=0)
        products = products.annotate(
            calculated_full_price=ExpressionWrapper(
                F('price') * (Value(100) - Coalesce(F('discount'), Value(0))) / Value(100),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )
        characteristics = subcategory.characteristics.all()
        for characteristic in characteristics:
            selected_values = filters.get(characteristic.slug)
            if selected_values:
                products = products.filter(
                    product_characteristics__characteristic=characteristic,
                    product_characteristics__value__in=selected_values
                )
        brands = filters.get('brand')
        if brands:
            products = products.filter(brand__slug__in=brands)

        price_from = filters.get('price_from')
        price_to = filters.get('price_to')
        if price_from is not None:
            products = products.filter(calculated_full_price__gte=Decimal(price_from))
        if price_to is not None:
            products = products.filter(calculated_full_price__lte=Decimal(price_to))
        if sort_option:
            products = sort_with_option(sort_option, products)

        return (products
            .select_related('brand','category','user')
            .prefetch_related('tags', get_prefetched_images_query(), get_prefetched_characteristics_query()))
    
    def get_context_data(self, **kwargs):
        subcategory = Category.objects.get(slug=self.kwargs['subcategory_slug'])
        session_key = f"ui_state:subcategory:{subcategory.slug}"
        ui_state = self.request.session.get(session_key, {})
        print(self.request.session.get(f"ui_state:subcategory:{subcategory.slug}", {}))
        context = super().get_context_data(**kwargs)
        context['title'] = subcategory.title
        context['subcategory'] = subcategory
        characteristics = (
            subcategory.characteristics
            .prefetch_related(
                Prefetch(
                    'product_characteristics',
                    queryset=(
                        ProductCharacteristic.objects
                        .filter(product__category=subcategory)
                        .select_related('product')
                        .only('id', 'value', 'product__id', 'product__slug')
                        .order_by('value')
                    ),
                    to_attr='prefetched_values'
                )
            )
        )
        context['characteristics'] = characteristics
        brands = Brand.objects.filter(products__category=subcategory).distinct()
        context['brands'] = brands
        qs = Product.objects.filter(category=subcategory, is_active=True, quantity__gt=0)
        discounted = ExpressionWrapper(
            F('price') * (Value(100) - Coalesce(F('discount'), Value(0))) / Value(100),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
        price_range = qs.aggregate(min_price=Min(discounted), max_price=Max(discounted))
        context.update(price_range)
        selected_filters = {}
        for characteristic in characteristics:
            values = ui_state.get(characteristic.slug)
            if values:
                selected_filters[characteristic.slug] = set(values)
        context['selected_filters'] = selected_filters
        context['selected_brands'] = ui_state.get('brand', [])
        context['saved_ui_state'] = ui_state
        return context

class SubcategoryProductsView(DetailView):
    model = Category
    template_name = 'products/components/_modal_window_for_subcategory.html'
    context_object_name = 'subcategory'
    slug_url_kwarg = 'slug'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = (self.object.products
                            .filter(is_active=True, quantity__gt=0)
                            .select_related('brand','category','user')
                            .prefetch_related('images','tags', get_prefetched_images_query())
                            [:6])
        return context
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        html = render_to_string(self.template_name, context, request=request)
        return HttpResponse(html)
    


class TagProductsView(DetailView):
    model = CustomTag
    template_name = 'products/components/_modal_window_for_tags.html'
    context_object_name = 'tag'
    slug_url_kwarg = 'tag_slug'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['products'] = Product.objects.filter(
            tags__in=[self.object],
            is_active=True,
            quantity__gt=0
        ).select_related('brand','category','user').prefetch_related('images','tags', get_prefetched_images_query()).exclude(slug=self.kwargs.get('product_slug')).distinct()[:5]
        return context
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        html = render_to_string(self.template_name, context, request=request)
        return HttpResponse(html)
    
def get_characteristics(request):
    category_id = request.GET.get('category_id')
    characteristics = Characteristic.objects.filter(category_id=category_id).values('id', 'title')
    return JsonResponse({'characteristics': list(characteristics)})


def subscribe_brand(request):
    if not request.user.is_authenticated:
        login_url = resolve_url(settings.LOGIN_URL)
        next_url = request.META.get("HTTP_REFERER") or request.get_full_path()
        return JsonResponse(
            {"status": "unauthorized", "login_url": f"{login_url}?{urlencode({'next': next_url})}"},
            status=401
        )
    if request.method == "POST":
        brand_id = request.POST.get('id')
        action = request.POST.get('action')
        try:
            brand = Brand.objects.get(id=brand_id)
            if action == "subscribe":
                Subcription.objects.get_or_create(user=request.user, brand=brand)
                return JsonResponse({'status': 'ok', 'action': 'subscribed'})
            else:
                Subcription.objects.filter(user=request.user, brand=brand).delete()
                return JsonResponse({'status': 'ok', 'action': 'unsubscribed'})
        except Brand.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Brand not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)