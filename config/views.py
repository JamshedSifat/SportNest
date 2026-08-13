# config/views.py

from django.shortcuts import render
from shop.models import MainCategory, Product

def home_view(request):
    """Home page with categories and offer products"""
    main_categories = MainCategory.objects.filter(is_active=True).order_by('order')
    
    # Get top 9 discount products
    offer_products = Product.objects.filter(
        is_active=True,
        discount_percentage__gt=0
    ).select_related('brand').order_by('-discount_percentage')[:9]

      # Latest 8 products (New Arrivals)
      
    new_arrivals = Product.objects.filter(
        is_active=True
    ).select_related('brand').order_by('-created_at')[:8]
    context = {
        'main_categories': main_categories,
        'offer_products': offer_products,
        'new_arrivals': new_arrivals,
    }
    return render(request, 'home.html', context)