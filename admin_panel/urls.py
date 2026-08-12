from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.admin_login_view, name='login'),
    path('logout/', views.admin_logout_view, name='logout'),

    # Product CRUD
    path('products/', views.products_view, name='products'),
    path('products/create/', views.product_create_view, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit_view, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete_view, name='product_delete'),
    path('product-images/<int:pk>/delete/', views.product_image_delete_view, name='product_image_delete'),

    # Category CRUD
    path('categories/', views.categories_view, name='categories'),
    path('categories/create/', views.category_create_view, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit_view, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete_view, name='category_delete'),

    # Subcategory CRUD
    path('subcategories/create/', views.subcategory_create_view, name='subcategory_create'),
    path('subcategories/<int:pk>/edit/', views.subcategory_edit_view, name='subcategory_edit'),
    path('subcategories/<int:pk>/delete/', views.subcategory_delete_view, name='subcategory_delete'),

    # Brand CRUD
    path('brands/', views.brands_view, name='brands'),
    path('brands/create/', views.brand_create_view, name='brand_create'),
    path('brands/<int:pk>/edit/', views.brand_edit_view, name='brand_edit'),
    path('brands/<int:pk>/delete/', views.brand_delete_view, name='brand_delete'),

    # Other pages
    path('customers/', views.customers_view, name='customers'),
    path('orders/', views.orders_view, name='orders'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('sales/', views.sales_view, name='sales'),
     path('orders/', views.orders_view, name='orders'),
    path('orders/<str:order_number>/', views.admin_order_detail, name='order_detail'),
    path('orders/bulk-action/', views.admin_orders_bulk_action, name='orders_bulk_action'),
]