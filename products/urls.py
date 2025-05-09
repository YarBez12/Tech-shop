from django.urls import path
from .views import *


app_name = 'products'


urlpatterns = [
    path('product/<slug:product_slug>/', ProductDetailView.as_view(), name = 'product_detail'),
    path('subscribe-brand/', subscribe_brand, name='subscribe_brand'),
    path('save-sort/<str:key>/', save_sort, name='save_sort'),
    path('save-filters/', save_filters, name="save_filters"),
    path('save-tab/<str:key>/', save_tab, name='save_tab'),
    path('save-rating/', save_rating, name='save_rating'),
    path('reset-filters/<slug:category_slug>/<slug:subcategory_slug>/', reset_filters, name='reset_filters'),
    path('review/<int:pk>/delete/', ReviewDelete.as_view(), name='review_delete'),
    path('review/<int:pk>/update/', ReviewEdit.as_view(), name='review_edit'),
    path('search-suggestions/', search_suggestions, name='search_suggestions'),
    path('search/', SearchResults.as_view(), name='search_results'),
    path('favourites/add/<slug:product_slug>/', add_to_favourites, name = 'add_to_favourites'),
    path('favourites/remove/<slug:product_slug>/', remove_from_favourites, name = 'remove_from_favourites'),
    path('favourites/', FavouriteProducts.as_view(), name = 'favourites'),
    path('subcategory/<slug:slug>/products/', SubcategoryProductsView.as_view(), name='subcategory_products'),
    path('product/<slug:product_slug>/<slug:tag_slug>/same/', TagProductsView.as_view(), name='tag_products'),
    path('brand/<slug:slug>', BrandDetails.as_view(), name='brand_details'),
    path('<slug:category_slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('<slug:category_slug>/<slug:subcategory_slug>/', SubcategoryDetailView.as_view(), name='subcategory_detail'),
]
