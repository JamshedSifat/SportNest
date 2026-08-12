
from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.shop_home, name='shop_home'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('subcategory/<slug:slug>/', views.subcategory_detail, name='subcategory_detail'),
    path('products/', views.all_products, name='all_products'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # cart
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<slug:slug>/', views.cart_update, name='cart_update'),
    path('cart/remove/<slug:slug>/', views.cart_remove, name='cart_remove'),
]