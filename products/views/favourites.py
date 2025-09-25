from products.models import Product
from django.core.paginator import EmptyPage, PageNotAnInteger
from products.utils.redis_utils import get_user_favourites, like_product, unlike_product
from products.utils.filters import sort_with_option
from products.utils.actions import create_action, delete_action
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from products.utils.mixins import EndlessPaginationMixin
from products.utils.filters import get_prefetched_characteristics_query



class FavouriteProducts(EndlessPaginationMixin, ListView):
    model = Product
    template_name = 'products/favourite_products.html'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        redis_product_ids = get_user_favourites(self.request.user.id)
        product_ids = [int(pid) for pid in redis_product_ids]
        products = (Product.objects
                    .filter(pk__in=product_ids, is_active=True, quantity__gt=0)
                    .select_related('brand','category','user')
                    .prefetch_related('images','tags', get_prefetched_characteristics_query()))
        session_key = "ui_state:favourite_products"
        ui_state = self.request.session.get(session_key, {})
        sort_option = ui_state.get('sort', 'title')
        return sort_with_option(sort_option, products) if sort_option else products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_key = "ui_state:favourite_products"
        ui_state = self.request.session.get(session_key, {})
        context['title'] = 'Favourite products'
        context['saved_ui_state'] = ui_state
        return context
    

@login_required    
def add_to_favourites(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    if not request.user == product.user:
        like_product(request.user.id, product.id)
        create_action(request.user, 'liked', product)
    next_page = request.META.get('HTTP_REFERER', '/')
    if "login" in next_page:
        next_page = product.get_absolute_url()
    return redirect (next_page)

@login_required    
def remove_from_favourites(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    unlike_product(request.user.id, product.id)
    delete_action(request.user, 'liked', product)
    next_page = request.META.get('HTTP_REFERER', '/')
    return redirect (next_page)   