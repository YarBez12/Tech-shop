from django.shortcuts import render
from products.models import Category, Product

# Create your views here.

def index(request):
    # parent_categories = Category.objects.filter(parent=None)
    # child_categories = Category.objects.exclude(parent = None)
    popular_products = Product.objects.order_by('-watched')[:12]
    context = {
        'title': 'Home Page',
        # 'parent_categories': parent_categories,
        # 'child_categories':child_categories,
        'popular_products': popular_products,
        'count_of_slides': (len(popular_products) // 4) 
    }
    return render(request, 'main/index.html', context)

