# from django.shortcuts import render, redirect
# from django.http import JsonResponse
# from .models import Characteristic, Category, Product, ReviewImage, Review, FavouriteProduct, CustomTag, Brand, Subcription, ProductImage, ProductActivationRequest
# from .forms import ReviewForm, ProductForm
# from django.views.generic import DetailView, ListView, DeleteView, UpdateView
# from django.views.generic.edit import FormMixin
# from django.contrib import messages
# from django.shortcuts import get_object_or_404
# from django.db.models.functions import Lower
# from django.db.models import Min, Max, Avg, Case, When, Value, BooleanField
# from django.db.models import Q, F
# from django.contrib.auth.decorators import login_required
# from django.template.loader import render_to_string
# from django.http import HttpResponse
# from django.db.models import Count
# from itertools import chain
# from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
# from django.core.paginator import EmptyPage, PageNotAnInteger
# from users.models import Action
# from django.contrib.contenttypes.models import ContentType
# import redis
# from django.conf import settings
# from django.views.decorators.csrf import csrf_exempt
# import json
# from decimal import Decimal
# from django.http import HttpResponseRedirect
# from .recommender import Recommender
# from django.urls import reverse
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.views import View
# from .utils.redis_utils import *
# from django.db.models import F, ExpressionWrapper, DecimalField, Value
# from django.db.models.functions import Coalesce, Lower





# r = redis.Redis.from_url(settings.REDIS_URL)

# # def get_characteristics(request):
# #     category_id = request.GET.get('category_id')
# #     characteristics = Characteristic.objects.filter(category_id=category_id).values('id', 'title')
# #     return JsonResponse({'characteristics': list(characteristics)})

# # class SearchResults(ListView):
# #     model = Product
# #     template_name = 'products/search_results.html'
# #     context_object_name = 'products'
# #     paginate_by = 2

# #     def get_queryset(self):
# #         session_key = "ui_state:search_results"
# #         ui_state = self.request.session.get(session_key, {})
# #         sort_option = ui_state.get('sort', 'title')
# #         search_query = self.request.GET.get('q', '').strip()
# #         products = filter_products(search_query)
# #         if sort_option:
# #             products = sort_with_option(sort_option, products)
# #         return products

# #     def get_template_names(self):
# #         if self.request.GET.get('products_only'):
# #             return ['products/components/_product_endless_list.html']  
# #         return [self.template_name]

# #     def get_context_data(self, **kwargs):
# #         context = super().get_context_data(**kwargs)
# #         search_query = self.request.GET.get('q', '').strip()
# #         categories = filter_categories(search_query).annotate(
# #             price=Avg(
# #                 ExpressionWrapper(
# #                 F('products__price') * (Value(100) - Coalesce(F('products__discount'), Value(0))) / Value(100),
# #                 output_field=DecimalField(max_digits=10, decimal_places=2)
# #                 )
# #             )
# #         )
# #         session_key = "ui_state:search_results"
# #         ui_state = self.request.session.get(session_key, {})
# #         context['saved_ui_state'] = ui_state
# #         sort_option = ui_state.get('sort', 'title')
# #         if sort_option:
# #             categories = sort_with_option(sort_option, categories)
# #         context['categories'] = categories
# #         context['title'] = 'Search results'
# #         context['is_search'] = True
# #         return context
    
# #     def render_to_response(self, context, **response_kwargs):
# #         page = context.get('page_obj')
# #         if self.request.GET.get('products_only') and (not page or not page.object_list):
# #             return HttpResponse('')
# #         return super().render_to_response(context, **response_kwargs)
    

# #     def paginate_queryset(self, queryset, page_size):
# #         paginator = self.get_paginator(queryset, page_size)
# #         page = self.request.GET.get(self.page_kwarg) or 1
# #         try:
# #             page_number = paginator.validate_number(page)
# #             page_obj = paginator.page(page_number)
# #             return paginator, page_obj, page_obj.object_list, page_obj.has_other_pages()
# #         except (PageNotAnInteger, EmptyPage):
# #             if self.request.GET.get('products_only'):
# #                 return paginator, None, [], False
# #             raise





# # class BrandDetails(ListView):
# #     model = Product
# #     template_name = 'products/brand.html'
# #     context_object_name = 'products'
# #     paginate_by = 2

# #     def get_queryset(self):
# #         brand = Brand.objects.get(slug=self.kwargs['slug'])
# #         session_key = f"ui_state:brand:{brand.slug}"
# #         ui_state = self.request.session.get(session_key, {})
# #         sort_option = ui_state.get('sort', 'title')
# #         products = Product.objects.filter(
# #             brand__slug=self.kwargs['slug'],
# #             is_active=True,
# #             quantity__gt=0
# #         )
# #         if sort_option:
# #             products = sort_with_option(sort_option, products)
# #         return products

# #     def get_template_names(self):
# #         if self.request.GET.get('products_only'):
# #             return ['products/components/_product_endless_list.html']  
# #         return [self.template_name]

# #     def get_context_data(self, **kwargs):
# #         context = super().get_context_data(**kwargs)
# #         brand = Brand.objects.get(slug=self.kwargs['slug'])
# #         context['title'] = brand.name
# #         context['brand'] = brand
# #         context['is_brand'] = True
# #         session_key = f"ui_state:brand:{brand.slug}"
# #         ui_state = self.request.session.get(session_key, {})
# #         context['saved_ui_state'] = ui_state
# #         return context
    
# #     def render_to_response(self, context, **response_kwargs):
# #         page = context.get('page_obj')
# #         if self.request.GET.get('products_only') and (not page or not page.object_list):
# #             return HttpResponse('')
# #         return super().render_to_response(context, **response_kwargs)
    

# #     def paginate_queryset(self, queryset, page_size):
# #         paginator = self.get_paginator(queryset, page_size)
# #         page = self.request.GET.get(self.page_kwarg) or 1
# #         try:
# #             page_number = paginator.validate_number(page)
# #             page_obj = paginator.page(page_number)
# #             return paginator, page_obj, page_obj.object_list, page_obj.has_other_pages()
# #         except (PageNotAnInteger, EmptyPage):
# #             if self.request.GET.get('products_only'):
# #                 return paginator, None, [], False
# #             raise






    
# # class FavouriteProducts(ListView):
# #     model = Product
# #     template_name = 'products/favourite_products.html'
# #     context_object_name = 'products'
# #     paginate_by = 2

# #     def paginate_queryset(self, queryset, page_size):
# #         paginator = self.get_paginator(queryset, page_size,
# #             orphans=self.get_paginate_orphans(),
# #             allow_empty_first_page=self.get_allow_empty()
# #         )
# #         page_number = self.request.GET.get(self.page_kwarg, 1)
# #         try:
# #             page = paginator.page(page_number)
# #         except PageNotAnInteger:
# #             page = paginator.page(1)
# #         except EmptyPage:
# #             page = paginator.page(paginator.num_pages)
# #         return paginator, page, page.object_list, page.has_other_pages()

# #     def get_queryset(self):
# #         # fav_products = self.request.user.favourite_products.all()
# #         # product_ids = fav_products.values_list('product__pk', flat=True)
# #         # products = Product.objects.filter(pk__in=product_ids, is_active=True)
# #         redis_product_ids = get_user_favourites(self.request.user.id)
# #         product_ids = [int(pid) for pid in redis_product_ids]
# #         products = Product.objects.filter(pk__in=product_ids, is_active=True)
# #         session_key = "ui_state:favourite_products"
# #         ui_state = self.request.session.get(session_key, {})
# #         sort_option = ui_state.get('sort', 'title')
# #         if sort_option:
# #             products = sort_with_option(sort_option, products)
# #         return products

# #     def get_context_data(self, **kwargs):
# #         context = super().get_context_data(**kwargs)
# #         session_key = "ui_state:favourite_products"
# #         ui_state = self.request.session.get(session_key, {})
# #         context['title'] = 'Favourite products'
# #         context['saved_ui_state'] = ui_state
# #         return context

# # def filter_products(search_query):
# #     products = Product.objects.filter(is_active=True)
# #     if search_query:
# #         vector = SearchVector('title', weight='A') + \
# #              SearchVector('description', weight='B') + \
# #              SearchVector('tags__name', weight='C') + \
# #              SearchVector('sku', weight='A')

# #         query = SearchQuery(search_query)


# #         qs = Product.objects.annotate(
# #             rank=SearchRank(vector, query)
# #         ).filter(rank__gte=0.1).order_by('-rank')

# #         product_ids = qs.values('id').distinct()
# #         products = Product.objects.filter(id__in=product_ids, is_active=True)
# #     return products

# # def filter_categories(search_query):
# #     categories = Category.objects.all()
# #     if search_query:
# #         vector = SearchVector('title', weight='A')
# #         query = SearchQuery(search_query)
# #         # search_terms = search_query.split()
# #         # query = Q()
# #         # for term in search_terms:
# #         #     query |= Q(title__icontains=term)  
# #         # categories = categories.filter(query).distinct()
# #         categories = Category.objects.annotate(
# #             rank=SearchRank(vector, query)
# #         ).filter(rank__gte=0.1).distinct().order_by(F('parent').asc(nulls_first=True), '-rank')
# #     categories = categories.order_by(F('parent').asc(nulls_first=True))
# #     return categories


# # class CategoryDetailView(ListView):
# #     model = Category
# #     context_object_name = 'subcategories'
# #     template_name = 'products/category.html'

# #     def get_queryset(self):
# #         parent_category = Category.objects.get(slug=self.kwargs['category_slug'])
# #         subcategories = (
# #             Category.objects.filter(parent=parent_category)
# #             .annotate(
# #                 active_products=Count(
# #                     'products',
# #                     filter=Q(products__is_active=True, products__quantity__gt=0)
# #                 )
# #             )
# #             .filter(active_products__gt=0)
# #         )

# #         return subcategories
    
# #     def get_context_data(self, **kwargs):
# #         parent_category = Category.objects.get(slug=self.kwargs['category_slug'])
# #         context = super().get_context_data(**kwargs)
# #         context['title'] = parent_category.title
# #         return context

# # def sort_with_option(sort_option, items):
# #     model = items.model
# #     if sort_option in ['price', '-price']:
# #         model_fields = [f.name for f in model._meta.get_fields()]
# #         if 'price' in model_fields and 'discount' in model_fields:
# #             items = items.annotate(
# #                 calculated_full_price=ExpressionWrapper(
# #                     F('price') * (Value(100) - Coalesce(F('discount'), Value(0))) / Value(100),
# #                     output_field=DecimalField(max_digits=10, decimal_places=2)
# #                 )
# #             )
# #             if sort_option == 'price':
# #                 items = items.order_by('calculated_full_price')
# #             else:
# #                 items = items.order_by('-calculated_full_price')
# #         else:
# #             items = items.order_by(sort_option)
# #     elif sort_option == 'title':
# #         items = items.annotate(lower_title=Lower('title')).order_by('lower_title')
# #     elif sort_option == '-title':
# #         items = items.annotate(lower_title=Lower('title')).order_by('-lower_title')
# #     else:
# #         items = items.order_by(sort_option)
# #     return items

# # class SubcategoryDetailView(ListView):
# #     model = Product
# #     context_object_name = 'products'
# #     template_name = 'products/subcategory.html'
# #     paginate_by = 2

# #     def paginate_queryset(self, queryset, page_size):
# #         paginator = self.get_paginator(queryset, page_size,
# #             orphans=self.get_paginate_orphans(),
# #             allow_empty_first_page=self.get_allow_empty()
# #         )
# #         page_number = self.request.GET.get(self.page_kwarg, 1)
# #         try:
# #             page = paginator.page(page_number)
# #         except PageNotAnInteger:
# #             page = paginator.page(1)
# #         except EmptyPage:
# #             page = paginator.page(paginator.num_pages)
# #         return paginator, page, page.object_list, page.has_other_pages()

# #     def get_queryset(self):
# #         subcategory = Category.objects.get(slug=self.kwargs['subcategory_slug'])
# #         session_key = f"ui_state:subcategory:{subcategory.slug}"
# #         ui_state = self.request.session.get(session_key, {})
# #         sort_option = ui_state.get('sort', 'title')
# #         filters = {k: v for k, v in ui_state.items() if k != 'sort'}
# #         products = Product.objects.filter(category=subcategory, is_active=True, quantity__gt=0)
# #         products = products.annotate(
# #             calculated_full_price=ExpressionWrapper(
# #                 F('price') * (Value(100) - Coalesce(F('discount'), Value(0))) / Value(100),
# #                 output_field=DecimalField(max_digits=10, decimal_places=2)
# #             )
# #         )
# #         characteristics = subcategory.characteristics.all()
# #         for characteristic in characteristics:
# #             selected_values = filters.get(characteristic.slug)
# #             if selected_values:
# #                 products = products.filter(
# #                     product_characteristics__characteristic=characteristic,
# #                     product_characteristics__value__in=selected_values
# #                 )
# #         brands = filters.get('brand')
# #         if brands:
# #             products = products.filter(brand__slug__in=brands)

# #         price_from = filters.get('price_from')
# #         price_to = filters.get('price_to')
# #         # if isinstance(price_from, list):
# #         #     price_from = price_from[0]
# #         # if isinstance(price_to, list):
# #         #     price_to = price_to[0]
# #         if price_from is not None:
# #             products = products.filter(calculated_full_price__gte=Decimal(price_from))
# #             # products = products.filter(price__gte=float(price_from))
# #         if price_to is not None:
# #             products = products.filter(calculated_full_price__lte=Decimal(price_to))
# #             # products = products.filter(price__lte=float(price_to))
# #         if sort_option:
# #             products = sort_with_option(sort_option, products)

# #         return products
    
# #     def get_context_data(self, **kwargs):
# #         subcategory = Category.objects.get(slug=self.kwargs['subcategory_slug'])
# #         session_key = f"ui_state:subcategory:{subcategory.slug}"
# #         ui_state = self.request.session.get(session_key, {})
# #         print(self.request.session.get(f"ui_state:subcategory:{subcategory.slug}", {}))
# #         context = super().get_context_data(**kwargs)
# #         context['title'] = subcategory.title
# #         context['subcategory'] = subcategory
# #         characteristics = subcategory.characteristics.all()
# #         context['characteristics'] = characteristics
# #         brands = Brand.objects.filter(products__category=subcategory).distinct()
# #         context['brands'] = brands
# #         qs = Product.objects.filter(category=subcategory, is_active=True)
# #         price_range = qs.aggregate(min_price=Min('price'), max_price=Max('price'))
# #         context.update(price_range)
# #         selected_filters = {}
# #         for characteristic in characteristics:
# #             values = ui_state.get(characteristic.slug)
# #             if values:
# #                 selected_filters[characteristic.slug] = set(values)
# #         # characteristic_slugs = {c.slug for c in characteristics}
# #         # for key, values in self.request.GET.lists():
# #         #     if key in characteristic_slugs:
# #         #         selected_filters[key] = set(values)
# #         context['selected_filters'] = selected_filters
# #         context['selected_brands'] = ui_state.get('brand', [])
# #         context['saved_ui_state'] = ui_state
# #         return context

# # class SubcategoryProductsView(DetailView):
# #     model = Category
# #     template_name = 'products/components/_modal_window_for_subcategory.html'
# #     context_object_name = 'subcategory'
# #     slug_url_kwarg = 'slug'


# #     def get_context_data(self, **kwargs):
# #         context = super().get_context_data(**kwargs)
# #         context['products'] = self.object.products.filter(is_active=True, quantity__gt=0)[:6]
# #         return context
# #     def get(self, request, *args, **kwargs):
# #         self.object = self.get_object()
# #         context = self.get_context_data()
# #         html = render_to_string(self.template_name, context, request=request)
# #         return HttpResponse(html)
    


# # class TagProductsView(DetailView):
# #     model = CustomTag
# #     template_name = 'products/components/_modal_window_for_tags.html'
# #     context_object_name = 'tag'
# #     slug_url_kwarg = 'tag_slug'


# #     def get_context_data(self, **kwargs):
# #         context = super().get_context_data(**kwargs)

# #         context['products'] = Product.objects.filter(
# #             tags__in=[self.object],
# #             is_active=True,
# #             quantity__gt=0
# #         ).exclude(slug=self.kwargs.get('product_slug')).distinct()[:5]
# #         return context
# #     def get(self, request, *args, **kwargs):
# #         self.object = self.get_object()
# #         context = self.get_context_data()
# #         html = render_to_string(self.template_name, context, request=request)
# #         return HttpResponse(html)

# class ProductDetailView(DetailView, FormMixin):
#     model = Product
#     template_name = 'products/product.html'
#     context_object_name = 'product'
#     form_class = ReviewForm

#     def get_success_url(self):
#         return self.request.path_info

#     def get_object(self, queryset = ...):
#         return Product.objects.get(slug=self.kwargs['product_slug'])
    
#     def get_context_data(self, **kwargs):
#         # Product.objects.filter(slug=self.kwargs['product_slug']).update(watched = F('watched') + 1)
#         self.object = self.get_object()
#         if not self.request.GET:
#             zincrby_product_view(self.object.id)
#             zincrby_category_view(self.object.category.id)
#         context = super().get_context_data(**kwargs)
#         r = Recommender()
#         recommended_bought_products = r.suggest_products_for([self.object], 8)
#         recommended_tag_related_products = Product.objects.exclude(pk=self.object.pk)\
#             .filter(tags__in=self.object.tags.all(), is_active=True)\
#             .annotate(same_tags=Count('tags', filter=Q(tags__in=self.object.tags.all())))\
#             .order_by('-same_tags')\
#             .distinct()
#         recommended_category_related_products = Product.objects.filter(category=self.object.category, is_active=True)\
#             .exclude(pk=self.object.pk)\
#             .exclude(id__in=recommended_tag_related_products.values_list('id', flat=True))
#         recommended_products = list(chain(recommended_bought_products, recommended_tag_related_products, recommended_category_related_products))[:8]
#         # filter_option = int(self.request.GET.get('rating', '0'))
#         product = self.get_object()
#         session_key = f"ui_state:product:{product.slug}"
#         ui_state = self.request.session.get(session_key, {})
#         rating = ui_state.get('rating')
#         reviews = (product.reviews.all().annotate(
#             is_current_user = Case(
#                 When(user=self.request.user, then=Value(True)),
#                 default=Value(False),
#                 output_field=BooleanField()
#             )
#         )
#         .order_by('-is_current_user'))
#         if rating:
#             reviews = reviews.filter(grade=rating)
#         context['reviews'] = reviews
#         context['title'] = self.object.title
#         context['review_form'] = self.get_form()
#         context['recommended_products'] = recommended_products
#         context['small_images'] = self.object.images.all()[1:4]
#         context['product_views'] = get_product_views(self.object.id)
#         context['ui_state'] = ui_state
#         return context
    
#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         form = self.get_form()
#         if form.is_valid():
#             review = form.save(commit=False)
#             review.product = self.object
#             review.user = request.user
#             review.save()
#             images = request.FILES.getlist('images')
#             for image in images:
#                 ReviewImage.objects.create(review=review, image=image)
#             messages.success(self.request, 'Your review has succesfully added')
#             return self.form_valid(form)
#         else:
#             error_messages = []
#             for field, errors in form.errors.items():
#                 field_label = field if field != '__all__' else 'General'
#                 error_messages.append(f"{field_label}: {', '.join(errors)}")
#             full_error_message = "Please correct the following errors: " + "; ".join(error_messages)
#             messages.error(self.request, full_error_message)
#             return self.form_invalid(form)
        
# # class ReviewDelete(DeleteView):
# #     model = Review
# #     context_object_name = 'review'
# #     extra_context = {
# #         'title': 'Review delete'
# #     }
    
# #     def get_success_url(self):
# #         messages.warning(self.request, 'Review has been deleated', extra_tags='deleted')
# #         return self.object.get_absolute_url()
    

# # class ProductDeactivate(LoginRequiredMixin, View):

# #     template_name = "products/product_deactivate_confirm.html"

# #     def get(self, request, product_slug):
# #         product = get_object_or_404(Product, slug=product_slug, user=request.user)
# #         context = {
# #             "product": product,
# #             "title": "Deactivate product",
# #         }
# #         return render(request, self.template_name, context)

# #     def post(self, request, product_slug):
# #         product = get_object_or_404(Product, slug=product_slug, user=request.user)
# #         product.is_active = False
# #         product.quantity = 0
# #         product.save(update_fields=["is_active", "quantity"])

# #         messages.warning(request, "Product has been deactivated (hidden from catalog).", extra_tags="deleted",)
# #         return redirect(self.get_success_url())

# #     def get_success_url(self):
# #         return reverse("users:profile")
    


# # class RequestActivationView(LoginRequiredMixin, View):
# #     def post(self, request, product_slug):
# #         product = get_object_or_404(Product, slug=product_slug)

# #         if product.is_active:
# #             messages.info(request, "The product is already active.")
# #             return redirect(product.get_absolute_url())
# #         exists = ProductActivationRequest.objects.filter(
# #             product=product, user=request.user, status='pending'
# #         ).exists()
# #         if exists:
# #             messages.info(request, "You already have a pending activation request for this product.")
# #             return redirect(product.get_absolute_url())

# #         req = ProductActivationRequest.objects.create(
# #             product=product, user=request.user, status='pending'
# #         )

# #         messages.success(request, "Activation request has been sent. We'll review it soon.")
# #         return redirect(product.get_absolute_url())
# # class ProductEdit(UpdateView):
# #     model = Product
# #     form_class = ProductForm
# #     template_name = 'products/product_edit.html'
# #     extra_context = {
# #         'title': 'Update review'
# #     }
# #     def get_context_data(self, **kwargs):
# #         context = super().get_context_data(**kwargs)
# #         context['product_form'] = context.get('form')
# #         context['existing_images'] = self.object.images.all()
# #         return context
    
# #     def form_valid(self, form):
# #         response = super().form_valid(form)
        
# #         new_images = self.request.FILES.getlist('images')
# #         for image in new_images:
# #             self.object.images.create(image=image)
        
# #         delete_images_ids = self.request.POST.getlist('delete_images')
# #         for image_id in delete_images_ids:
# #             image = get_object_or_404(ProductImage, id=image_id)
# #             image.delete()
# #         messages.success(self.request, 'Product has been updated')
        
# #         return response
# #     def form_invalid(self, form):
# #         response = super().form_invalid(form)
# #         error_messages = []
# #         for field, errors in form.errors.items():
# #             field_label = field if field != '__all__' else 'General'
# #             error_messages.append(f"{field_label}: {', '.join(errors)}")
# #         full_error_message = "Please correct the following errors: " + "; ".join(error_messages)
# #         messages.error(self.request, full_error_message)

# #         return response
    
# # class ReviewEdit(UpdateView):
# #     model = Review
# #     form_class = ReviewForm
# #     template_name = 'products/review_edit.html'
# #     extra_context = {
# #         'title': 'Review update'
# #     }
# #     def get_context_data(self, **kwargs):
# #         context = super().get_context_data(**kwargs)
# #         context['review_form'] = context.get('form')
# #         context['existing_images'] = self.object.images.all()
# #         return context
    
# #     def form_valid(self, form):
# #         response = super().form_valid(form)
        
# #         new_images = self.request.FILES.getlist('images')
# #         for image in new_images:
# #             self.object.images.create(image=image)
        
# #         delete_images_ids = self.request.POST.getlist('delete_images')
# #         for image_id in delete_images_ids:
# #             image = get_object_or_404(ReviewImage, id=image_id)
# #             image.delete()
# #         messages.success(self.request, 'Review has been updated')
        
# #         return response
# #     def form_invalid(self, form):
# #         response = super().form_invalid(form)
# #         error_messages = []
# #         for field, errors in form.errors.items():
# #             field_label = field if field != '__all__' else 'General'
# #             error_messages.append(f"{field_label}: {', '.join(errors)}")
# #         full_error_message = "Please correct the following errors: " + "; ".join(error_messages)
# #         messages.error(self.request, full_error_message)

# #         return response
    
    
# # def search_suggestions(request):
# #     search_query = request.GET.get('q', '').strip()
# #     if not search_query:
# #         return JsonResponse({'categories': [], 'products': []})
# #     categories = filter_categories(search_query)
# #     if len(categories) >= 10:
# #         return JsonResponse({
# #         'categories': [
# #             {
# #                 'title': category.title,
# #                 'url': category.get_absolute_url(),
# #             } for category in categories[:10]
# #         ],
# #         'products': [] 
# #     })
# #     else:
# #         products = filter_products(search_query)
# #         return JsonResponse({
# #             'categories': [
# #             {
# #                 'title': category.title,
# #                 'url': category.get_absolute_url(),
# #             } for category in categories
# #             ],
# #             'products': [
# #             {
# #                 'title': product.title,
# #                 'url': product.get_absolute_url(),
# #             } for product in products[:(10-len(categories))]
# #             ] 
# #         })

# # @login_required    
# # def add_to_favourites(request, product_slug):
# #     product = get_object_or_404(Product, slug=product_slug)
# #     if not request.user == product.user:
# #         like_product(request.user.id, product.id)
# #         create_action(request.user, 'liked', product)
# #     next_page = request.META.get('HTTP_REFERER', '/')
# #     if "login" in next_page:
# #         next_page = product.get_absolute_url()
# #     return redirect (next_page)

# # @login_required    
# # def remove_from_favourites(request, product_slug):
# #     product = get_object_or_404(Product, slug=product_slug)
# #     unlike_product(request.user.id, product.id)
# #     delete_action(request.user, 'liked', product)
# #     next_page = request.META.get('HTTP_REFERER', '/')
# #     return redirect (next_page)   

# # @login_required
# # def subscribe_brand(request):
# #     if request.method == "POST":
# #         brand_id = request.POST.get('id')
# #         action = request.POST.get('action')
# #         try:
# #             brand = Brand.objects.get(id=brand_id)
# #             if action == "subscribe":
# #                 Subcription.objects.get_or_create(user=request.user, brand=brand)
# #                 return JsonResponse({'status': 'ok', 'action': 'subscribed'})
# #             else:
# #                 Subcription.objects.filter(user=request.user, brand=brand).delete()
# #                 return JsonResponse({'status': 'ok', 'action': 'unsubscribed'})
# #         except Brand.DoesNotExist:
# #             return JsonResponse({'status': 'error', 'message': 'Brand not found'})
# #     return JsonResponse({'status': 'error', 'message': 'Invalid request'})



# # def create_action(user, verb, target=None):
# #     existing = Action.objects.filter(user=user, verb=verb)
# #     if target:
# #         ct = ContentType.objects.get_for_model(target)
# #         existing = existing.filter(target_ct=ct, target_id=target.id)
# #     if existing.exists():
# #         return False

# #     action = Action(user=user, verb=verb, target=target)
# #     action.save()
# #     return True

# # def delete_action(user, verb, target=None):
# #     actions = Action.objects.filter(user=user, verb=verb)
# #     if target:
# #         ct = ContentType.objects.get_for_model(target)
# #         actions = actions.filter(target_ct=ct, target_id=target.id)
# #     actions.delete()





# # @csrf_exempt
# # def save_filters(request):
# #     if request.method == "POST":
# #         data = json.loads(request.body)
# #         slug = data.pop("slug", None)  
# #         session_key = f"ui_state:subcategory:{slug}"
# #         ui_state = request.session.get(session_key, {})
# #         sort = ui_state.get("sort")
# #         ui_state = {}
# #         if sort:
# #             ui_state["sort"] = sort
# #         for key, value in data.items():
# #             if key in ['price_from', 'price_to']:
# #                 ui_state[key] = value
# #             else:
# #                 if isinstance(value, str):
# #                     value = [value]
# #                 ui_state[key] = value
# #         request.session[session_key] = ui_state
# #         request.session.modified = True
# #         return JsonResponse({"status": "ok"})
# #     return JsonResponse({"status": "error"}, status=400)


# # def reset_filters(request, category_slug, subcategory_slug):
# #     session_key = f"ui_state:subcategory:{subcategory_slug}"
# #     if session_key in request.session:
# #         del request.session[session_key]
# #         request.session.modified = True
# #     return redirect('products:subcategory_detail', category_slug=category_slug, subcategory_slug=subcategory_slug)


# # @csrf_exempt
# # def save_sort(request, key):
# #     if request.method == "POST":
# #         data = json.loads(request.body)
# #         sort_value = data.get("sort")
# #         slug = data.get("slug")
# #         session_key = f"ui_state:{key}" + (f":{slug}" if slug else "")
# #         print(session_key)
# #         ui_state = request.session.get(session_key, {})
# #         ui_state["sort"] = sort_value
# #         request.session[session_key] = ui_state
# #         request.session.modified = True
# #         return JsonResponse({"status": "ok"})
# #     return JsonResponse({"status": "error"}, status=400)


# # @csrf_exempt
# # def save_tab(request, key):
# #     if request.method == "POST":
# #         data = json.loads(request.body)
# #         slug = data.get("slug")
# #         tab = data.get("tab")
# #         session_key = f"ui_state:{key}" + (f":{slug}" if slug else "")
# #         ui_state = request.session.get(session_key, {})
# #         ui_state["tab"] = tab
# #         request.session[session_key] = ui_state
# #         request.session.modified = True
# #         return JsonResponse({"status": "ok"})
# #     return JsonResponse({"status": "error"}, status=400)


# # @csrf_exempt
# # def save_rating(request):
# #     if request.method == "POST":
# #         data = json.loads(request.body)
# #         slug = data.get("slug")
# #         rating = data.get("rating")
# #         session_key = f"ui_state:product:{slug}"
# #         ui_state = request.session.get(session_key, {})
# #         if rating is None:
# #             ui_state.pop("rating", None)
# #         else:
# #             ui_state["rating"] = rating
# #         request.session[session_key] = ui_state
# #         request.session.modified = True
# #         return JsonResponse({"status": "ok"})
# #     return JsonResponse({"status": "error"}, status=400)

