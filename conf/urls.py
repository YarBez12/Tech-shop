"""
URL configuration for conf project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from conf import settings
from django.conf.urls.static import static
from products.views.catalog import get_characteristics
from django.conf.urls import handler404
from main.views import custom_404, test_404
from django.contrib.sitemaps.views import sitemap
from main.sitemaps import ProductSitemap
from main.views_internal import run_sync



sitemaps = {
    'products': ProductSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('internal/sync/', run_sync, name='internal-sync'),
    path('test-404/', test_404),
    path('admin/get_characteristics/', get_characteristics, name='get_characteristics'),
    path('sitemap.xml/', sitemap, {'sitemaps': sitemaps}, name = 'django.contrib.sitemaps.views.sitemap'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('coupons/', include('coupons.urls', namespace='coupons')),
    path('course/', include('courses.urls', namespace='courses')),
    path('', include('main.urls', namespace='main')),
    path('user/', include('users.urls', namespace='users')),
    path('products/', include('products.urls', namespace='products')),
    path('cart/', include('carts.urls', namespace='carts')),
    path('students/', include('students.urls', namespace='students'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]


handler404 = custom_404
