from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Characteristic, Category, Product, ReviewImage, Review, FavouriteProduct
from .forms import ReviewForm
from django.views.generic import DetailView, ListView, DeleteView, UpdateView
from django.views.generic.edit import FormMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models.functions import Lower
from django.db.models import Min, Max, Avg
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required




def get_characteristics(request):
    category_id = request.GET.get('category_id')
    characteristics = Characteristic.objects.filter(category_id=category_id).values('id', 'title')
    return JsonResponse({'characteristics': list(characteristics)})

class SearchResults(ListView):
    model = Product
    template_name = 'products/search_results.html'
    context_object_name = 'products'
    paginate_by = 2

    def get_queryset(self):
        sort_option = self.request.GET.get('sort', 'title')
        search_query = self.request.GET.get('q', '').strip()
        products = filter_products(search_query)
        if sort_option:
            products = sort_with_option(sort_option, products)
        return products

    def get_context_data(self, **kwargs):
        sort_option = self.request.GET.get('sort', 'title')
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q', '').strip()
        categories = filter_categories(search_query).annotate(price=Avg('products__price'))
        if sort_option:
            categories = sort_with_option(sort_option, categories)
        context['categories'] = categories
        context['title'] = 'Search results'
        context['is_search'] = True
        return context
    
class FavouriteProducts(ListView):
    model = Product
    template_name = 'products/favourite_products.html'
    context_object_name = 'products'
    paginate_by = 2
    extra_context = {
        'title': 'Favourite products'
    }

    def get_queryset(self):
        sort_option = self.request.GET.get('sort', 'title')
        fav_products = self.request.user.favourite_products.all()
        product_ids = fav_products.values_list('product__pk', flat=True)
        products = Product.objects.filter(pk__in=product_ids)
        if sort_option:
            products = sort_with_option(sort_option, products)
        return products

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['title'] = 'Favourite products'
    #     return context

def filter_products(search_query):
    products = Product.objects.all()
    if search_query:
        search_terms = search_query.split()
        query = Q()
        for term in search_terms:
            query |= Q(title__icontains=term)  
            query |= Q(description__icontains=term)  
            query |= Q(tags__tag__icontains=term)
            query |= Q(sku__icontains=term)
        products = products.filter(query).distinct()
    return products

def filter_categories(search_query):
    categories = Category.objects.all()
    if search_query:
        search_terms = search_query.split()
        query = Q()
        for term in search_terms:
            query |= Q(title__icontains=term)  
        categories = categories.filter(query).distinct()
    categories = categories.order_by(F('parent').asc(nulls_first=True))
    return categories


class CategoryDetailView(ListView):
    model = Category
    context_object_name = 'subcategories'
    template_name = 'products/category.html'

    def get_queryset(self):
        parent_category = Category.objects.get(slug=self.kwargs['category_slug'])
        subcategories = Category.objects.filter(parent=parent_category)

        return subcategories
    
    def get_context_data(self, **kwargs):
        parent_category = Category.objects.get(slug=self.kwargs['category_slug'])
        context = super().get_context_data(**kwargs)
        context['title'] = parent_category.title
        return context
        
def sort_with_option(sort_option, items):
    if sort_option == 'title':
        items = items.annotate(lower_title=Lower('title')).order_by('lower_title')
    elif sort_option == '-title':
        items = items.annotate(lower_title=Lower('title')).order_by('-lower_title')
    else:
        items = items.order_by(sort_option)
    return items

class SubcategoryDetailView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'products/subcategory.html'
    paginate_by = 1

    def get_queryset(self):
        sort_option = self.request.GET.get('sort', 'title')
        subcategory = Category.objects.get(slug=self.kwargs['subcategory_slug'])
        products = Product.objects.filter(category=subcategory)
        characteristics = subcategory.characteristics.all()
        for characteristic in characteristics:
            selected_values = self.request.GET.getlist(characteristic.slug)
            if selected_values:
                products = products.filter(
                    product_characteristics__characteristic=characteristic,
                    product_characteristics__value__in=selected_values
                )

        price_from = self.request.GET.get('price_from')
        price_to = self.request.GET.get('price_to')
        if price_from is not None:
            products = products.filter(price__gte=float(price_from))
        if price_to is not None:
            products = products.filter(price__lte=float(price_to))
        if sort_option:
            products = sort_with_option(sort_option, products)

        return products
    
    def get_context_data(self, **kwargs):
        subcategory = Category.objects.get(slug=self.kwargs['subcategory_slug'])
        context = super().get_context_data(**kwargs)
        context['title'] = subcategory.title
        context['subcategory'] = subcategory
        context['characteristics'] = subcategory.characteristics.all()
        qs = Product.objects.filter(category=subcategory)
        price_range = qs.aggregate(min_price=Min('price'), max_price=Max('price'))
        context.update(price_range)
        selected_filters = {}
        for key, values in self.request.GET.lists():
            selected_filters[key] = set(values)
        context['selected_filters'] = selected_filters
        return context
    
class ProductDetailView(DetailView, FormMixin):
    model = Product
    template_name = 'products/product.html'
    context_object_name = 'product'
    form_class = ReviewForm

    def get_success_url(self):
        return self.request.path_info

    def get_object(self, queryset = ...):
        return Product.objects.get(slug=self.kwargs['product_slug'])
    
    def get_context_data(self, **kwargs):
        Product.objects.filter(slug=self.kwargs['product_slug']).update(watched = F('watched') + 1)
        context = super().get_context_data(**kwargs)
        recommended_products = Product.objects.filter(category=self.object.category).exclude(pk=self.object.pk)[:8]
        filter_option = int(self.request.GET.get('rating', '0'))
        product = self.get_object()
        reviews = product.reviews.all()
        if filter_option:
            reviews = reviews.filter(grade=filter_option)
        context['reviews'] = reviews
        context['title'] = self.object.title
        context['review_form'] = self.get_form()
        context['recommended_products'] = recommended_products
        context['small_images'] = self.object.images.all()[1:5]
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            review = form.save(commit=False)
            review.product = self.object
            review.user = request.user
            review.save()
            images = request.FILES.getlist('images')
            print(images)
            for image in images:
                ReviewImage.objects.create(review=review, image=image)
            messages.success(self.request, 'Your review has succesfully added')
            return self.form_valid(form)
        else:
            error_messages = []
            for field, errors in form.errors.items():
                field_label = field if field != '__all__' else 'General'
                error_messages.append(f"{field_label}: {', '.join(errors)}")
            full_error_message = "Please correct the following errors: " + "; ".join(error_messages)
            messages.error(self.request, full_error_message)
            return self.form_invalid(form)
        
class ReviewDelete(DeleteView):
    model = Review
    context_object_name = 'review'
    extra_context = {
        'title': 'Review delete'
    }
    
    def get_success_url(self):
        messages.warning(self.request, 'Review has been deleated', extra_tags='deleted')
        return self.object.get_absolute_url()
    
class ReviewEdit(UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'products/review_edit.html'
    extra_context = {
        'title': 'Review update'
    }
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_form'] = context.get('form')
        context['existing_images'] = self.object.images.all()
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        new_images = self.request.FILES.getlist('images')
        for image in new_images:
            self.object.images.create(image=image)
        
        delete_images_ids = self.request.POST.getlist('delete_images')
        for image_id in delete_images_ids:
            image = get_object_or_404(ReviewImage, id=image_id)
            image.delete()
        messages.success(self.request, 'Review has been updated')
        
        return response
    def form_invalid(self, form):
        response = super().form_invalid(form)
        error_messages = []
        for field, errors in form.errors.items():
            field_label = field if field != '__all__' else 'General'
            error_messages.append(f"{field_label}: {', '.join(errors)}")
        full_error_message = "Please correct the following errors: " + "; ".join(error_messages)
        messages.error(self.request, full_error_message)

        return response
    
    
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

@login_required    
def add_to_favourites(request, product_slug):
    product = Product.objects.get(slug=product_slug)
    user = request.user
    FavouriteProduct.objects.create(product=product, user=user)
    next_page = request.META.get('HTTP_REFERER', '/')
    if "login" in next_page:
        next_page = product.get_absolute_url()
    return redirect (next_page)

@login_required    
def remove_from_favourites(request, product_slug):
    product = Product.objects.get(slug=product_slug)
    user = request.user
    favs = FavouriteProduct.objects.filter(product=product, user=user)
    if favs:
        favs[0].delete()
    next_page = request.META.get('HTTP_REFERER', '/')
    return redirect (next_page)   
