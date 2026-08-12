# config/views.py

from django.shortcuts import render
from shop.models import MainCategory

def home_view(request):
    """Home page view with dynamic categories"""
    
    main_categories = MainCategory.objects.filter(is_active=True).order_by('order')
    
    print(f"Categories found: {main_categories.count()}")  # Debug line
    
    context = {
        'main_categories': main_categories,
    }
    
    return render(request, 'home.html', context)