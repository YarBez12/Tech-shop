from products.models import Product, Brand, Category, CustomTag, Characteristic, Subcription
from products.utils.filters import sort_with_option
from django.http import HttpResponse
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.db.models import F, ExpressionWrapper, DecimalField, Value, Count, Min, Max, Q
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, ListView



class BrandDetails(ListView):
    model = Product
    template_name = 'products/brand.html'
    context_object_name = 'products'
    paginate_by = 2

    def get_queryset(self):
        brand = Brand.objects.get(slug=self.kwargs['slug'])
        session_key = f"ui_state:brand:{brand.slug}"
        ui_state = self.request.session.get(session_key, {})
        sort_option = ui_state.get('sort', 'title')
        products = Product.objects.filter(
            brand__slug=self.kwargs['slug'],
            is_active=True,
            quantity__gt=0
        )
        if sort_option:
            products = sort_with_option(sort_option, products)
        return products

    def get_template_names(self):
        if self.request.GET.get('products_only'):
            return ['products/components/_product_endless_list.html']  
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand = Brand.objects.get(slug=self.kwargs['slug'])
        context['title'] = brand.name
        context['brand'] = brand
        context['is_brand'] = True
        session_key = f"ui_state:brand:{brand.slug}"
        ui_state = self.request.session.get(session_key, {})
        context['saved_ui_state'] = ui_state
        return context
    
    def render_to_response(self, context, **response_kwargs):
        page = context.get('page_obj')
        if self.request.GET.get('products_only') and (not page or not page.object_list):
            return HttpResponse('')
        return super().render_to_response(context, **response_kwargs)
    

    def paginate_queryset(self, queryset, page_size):
        paginator = self.get_paginator(queryset, page_size)
        page = self.request.GET.get(self.page_kwarg) or 1
        try:
            page_number = paginator.validate_number(page)
            page_obj = paginator.page(page_number)
            return paginator, page_obj, page_obj.object_list, page_obj.has_other_pages()
        except (PageNotAnInteger, EmptyPage):
            if self.request.GET.get('products_only'):
                return paginator, None, [], False
            raise


class CategoryDetailView(ListView):
    model = Category
    context_object_name = 'subcategories'
    template_name = 'products/category.html'

    def get_queryset(self):
        parent_category = Category.objects.get(slug=self.kwargs['category_slug'])
        subcategories = (
            Category.objects.filter(parent=parent_category)
            .annotate(
                active_products=Count(
                    'products',
                    filter=Q(products__is_active=True, products__quantity__gt=0)
                )
            )
            .filter(active_products__gt=0)
        )

        return subcategories
    
    def get_context_data(self, **kwargs):
        parent_category = Category.objects.get(slug=self.kwargs['category_slug'])
        context = super().get_context_data(**kwargs)
        context['title'] = parent_category.title
        return context
    

class SubcategoryDetailView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'products/subcategory.html'
    paginate_by = 2

    def paginate_queryset(self, queryset, page_size):
        paginator = self.get_paginator(queryset, page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty()
        )
        page_number = self.request.GET.get(self.page_kwarg, 1)
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        return paginator, page, page.object_list, page.has_other_pages()

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

        return products
    
    def get_context_data(self, **kwargs):
        subcategory = Category.objects.get(slug=self.kwargs['subcategory_slug'])
        session_key = f"ui_state:subcategory:{subcategory.slug}"
        ui_state = self.request.session.get(session_key, {})
        print(self.request.session.get(f"ui_state:subcategory:{subcategory.slug}", {}))
        context = super().get_context_data(**kwargs)
        context['title'] = subcategory.title
        context['subcategory'] = subcategory
        characteristics = subcategory.characteristics.all()
        context['characteristics'] = characteristics
        brands = Brand.objects.filter(products__category=subcategory).distinct()
        context['brands'] = brands
        qs = Product.objects.filter(category=subcategory, is_active=True)
        price_range = qs.aggregate(min_price=Min('price'), max_price=Max('price'))
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
        context['products'] = self.object.products.filter(is_active=True, quantity__gt=0)[:6]
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
        ).exclude(slug=self.kwargs.get('product_slug')).distinct()[:5]
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


@login_required
def subscribe_brand(request):
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
            return JsonResponse({'status': 'error', 'message': 'Brand not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})