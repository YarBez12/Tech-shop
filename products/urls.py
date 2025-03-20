from django.urls import path
from .views import *


app_name = 'products'


urlpatterns = [
    path('product/<slug:product_slug>/', ProductDetailView.as_view(), name = 'product_detail'),
    path('review/<int:pk>/delete/', ReviewDelete.as_view(), name='review_delete'),
    path('review/<int:pk>/update/', ReviewEdit.as_view(), name='review_edit'),
    path('search-suggestions/', search_suggestions, name='search_suggestions'),
    path('search/', SearchResults.as_view(), name='search_results'),
    path('favourites/add/<slug:product_slug>/', add_to_favourites, name = 'add_to_favourites'),
    path('favourites/remove/<slug:product_slug>/', remove_from_favourites, name = 'remove_from_favourites'),
    path('favourites/', FavouriteProducts.as_view(), name = 'favourites'),
    path('<slug:category_slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('<slug:category_slug>/<slug:subcategory_slug>/', SubcategoryDetailView.as_view(), name='subcategory_detail'),
]
