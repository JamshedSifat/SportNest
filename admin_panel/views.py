from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from orders.models import Order

from accounts.models import User
from shop.models import MainCategory, SubCategory, Brand, Product, ProductImage
from .forms import (
    AdminLoginForm,
    MainCategoryForm, SubCategoryForm,
    BrandForm, ProductForm, ProductImageForm
)


def staff_required(view_func):
    decorated_view = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url='admin_panel:login'
    )
    return decorated_view(view_func)


def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_panel:dashboard')

    if request.method == 'POST':
        form = AdminLoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None and user.is_staff:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or "Admin"}!')
                return redirect('admin_panel:dashboard')
            messages.error(request, 'Invalid email or password.')
    else:
        form = AdminLoginForm()

    return render(request, 'admin_panel/login.html', {'form': form})


@staff_required
def dashboard_view(request):
    stats = {
        'total_products': Product.objects.count(),
        'total_orders': 0,  # integrate order app later
        'total_customers': User.objects.filter(is_staff=False).count(),
        'total_revenue': 0,  # integrate order app later
        'new_orders_today': 0,
        'pending_orders': 0,
        'low_stock_products': Product.objects.filter(stock__lt=5, is_active=True).count(),
        'active_customers': User.objects.filter(is_active=True, is_staff=False).count(),
    }

    context = {
        'stats': stats,
        'recent_orders': [],
        'recent_customers': User.objects.filter(is_staff=False).order_by('-date_joined')[:5],
        'popular_products': Product.objects.filter(is_active=True).order_by('-created_at')[:5],
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ---------------- CATEGORIES CRUD ----------------
@staff_required
def categories_view(request):
    categories = MainCategory.objects.all().order_by('order', 'name')
    subcategories = SubCategory.objects.select_related('main_category').all().order_by('main_category__name', 'order', 'name')
    return render(request, 'admin_panel/categories.html', {
        'categories': categories,
        'subcategories': subcategories,
    })


@staff_required
def category_create_view(request):
    if request.method == 'POST':
        form = MainCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('admin_panel:categories')
    else:
        form = MainCategoryForm()
    return render(request, 'admin_panel/category_form.html', {'form': form, 'title': 'Create Category'})


@staff_required
def category_edit_view(request, pk):
    obj = get_object_or_404(MainCategory, pk=pk)
    if request.method == 'POST':
        form = MainCategoryForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('admin_panel:categories')
    else:
        form = MainCategoryForm(instance=obj)
    return render(request, 'admin_panel/category_form.html', {'form': form, 'title': 'Edit Category'})


@staff_required
def category_delete_view(request, pk):
    obj = get_object_or_404(MainCategory, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Category deleted.')
        return redirect('admin_panel:categories')
    return render(request, 'admin_panel/confirm_delete.html', {'object': obj, 'type': 'Category'})


# ---------------- SUBCATEGORIES CRUD ----------------
@staff_required
def subcategory_create_view(request):
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subcategory created successfully.')
            return redirect('admin_panel:categories')
    else:
        form = SubCategoryForm()
    return render(request, 'admin_panel/subcategory_form.html', {'form': form, 'title': 'Create Subcategory'})


@staff_required
def subcategory_edit_view(request, pk):
    obj = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subcategory updated successfully.')
            return redirect('admin_panel:categories')
    else:
        form = SubCategoryForm(instance=obj)
    return render(request, 'admin_panel/subcategory_form.html', {'form': form, 'title': 'Edit Subcategory'})


@staff_required
def subcategory_delete_view(request, pk):
    obj = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Subcategory deleted.')
        return redirect('admin_panel:categories')
    return render(request, 'admin_panel/confirm_delete.html', {'object': obj, 'type': 'Subcategory'})


# ---------------- BRANDS CRUD ----------------
@staff_required
def brands_view(request):
    brands = Brand.objects.all().order_by('name')
    return render(request, 'admin_panel/brands.html', {'brands': brands})


@staff_required
def brand_create_view(request):
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand created successfully.')
            return redirect('admin_panel:brands')
    else:
        form = BrandForm()
    return render(request, 'admin_panel/brand_form.html', {'form': form, 'title': 'Create Brand'})


@staff_required
def brand_edit_view(request, pk):
    obj = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand updated successfully.')
            return redirect('admin_panel:brands')
    else:
        form = BrandForm(instance=obj)
    return render(request, 'admin_panel/brand_form.html', {'form': form, 'title': 'Edit Brand'})


@staff_required
def brand_delete_view(request, pk):
    obj = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Brand deleted.')
        return redirect('admin_panel:brands')
    return render(request, 'admin_panel/confirm_delete.html', {'object': obj, 'type': 'Brand'})


# ---------------- PRODUCTS CRUD ----------------
@staff_required
def products_view(request):
    qs = Product.objects.select_related('subcategory', 'brand').all().order_by('-created_at')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(name__icontains=q)

    paginator = Paginator(qs, 20)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'admin_panel/products.html', {'products': products, 'q': q})


@staff_required
def product_create_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            # additional images
            images = request.FILES.getlist('extra_images')
            for idx, img in enumerate(images):
                ProductImage.objects.create(product=product, image=img, order=idx)
            messages.success(request, 'Product created successfully.')
            return redirect('admin_panel:products')
    else:
        form = ProductForm()

    return render(request, 'admin_panel/product_form.html', {'form': form, 'title': 'Create Product'})


@staff_required
def product_edit_view(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()

            # add new extra images
            images = request.FILES.getlist('extra_images')
            start_order = product.images.count()
            for idx, img in enumerate(images, start=start_order):
                ProductImage.objects.create(product=product, image=img, order=idx)

            messages.success(request, 'Product updated successfully.')
            return redirect('admin_panel:products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'admin_panel/product_form.html', {
        'form': form,
        'title': 'Edit Product',
        'product': product,
        'extra_images': product.images.all()
    })


@staff_required
def product_delete_view(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Product deleted.')
        return redirect('admin_panel:products')
    return render(request, 'admin_panel/confirm_delete.html', {'object': obj, 'type': 'Product'})


@staff_required
def product_image_delete_view(request, pk):
    img = get_object_or_404(ProductImage, pk=pk)
    product_id = img.product_id
    if request.method == 'POST':
        img.delete()
        messages.success(request, 'Image removed.')
        return redirect('admin_panel:product_edit', pk=product_id)
    return render(request, 'admin_panel/confirm_delete.html', {'object': img, 'type': 'Product Image'})


@staff_required
def customers_view(request):
    customers = User.objects.filter(is_staff=False).order_by('-date_joined')
    return render(request, 'admin_panel/customers.html', {'customers': customers})


@staff_required
def orders_view(request):
    return render(request, 'admin_panel/orders.html')


@staff_required
def inventory_view(request):
    products = Product.objects.filter(is_active=True).order_by('stock')
    return render(request, 'admin_panel/inventory.html', {'products': products})


@staff_required
def sales_view(request):
    return render(request, 'admin_panel/sales.html')


@staff_required
def admin_logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Logged out successfully.')
        return redirect('admin_panel:login')
    return render(request, 'admin_panel/logout.html')



    
# UPDATE the dashboard_view function
@staff_required
def dashboard_view(request):
    today = timezone.now().date()
    this_month = today.replace(day=1)
    
    # Order stats
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='PENDING').count()
    today_orders = Order.objects.filter(created_at__date=today).count()
    total_revenue = Order.objects.filter(
        status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    stats = {
        'total_products': Product.objects.count(),
        'total_orders': total_orders,
        'total_customers': User.objects.filter(is_staff=False).count(),
        'total_revenue': total_revenue,
        'new_orders_today': today_orders,
        'pending_orders': pending_orders,
        'low_stock_products': Product.objects.filter(stock__lt=5, is_active=True).count(),
        'active_customers': User.objects.filter(is_active=True, is_staff=False).count(),
    }

    context = {
        'stats': stats,
        'recent_orders': Order.objects.all().order_by('-created_at')[:10],
        'recent_customers': User.objects.filter(is_staff=False).order_by('-date_joined')[:5],
        'popular_products': Product.objects.filter(is_active=True).order_by('-created_at')[:5],
    }
    return render(request, 'admin_panel/dashboard.html', context)


# REPLACE the orders_view function
@staff_required
def orders_view(request):
    """Admin - All Orders with filters"""
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    orders = Order.objects.all().select_related('user').order_by('-created_at')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    if search:
        from django.db.models import Q
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(full_name__icontains=search) |
            Q(phone__icontains=search) |
            Q(email__icontains=search)
        )
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    
    # Stats
    total_orders = Order.objects.count()
    pending_count = Order.objects.filter(status='PENDING').count()
    today_count = Order.objects.filter(created_at__date=timezone.now().date()).count()
    revenue = Order.objects.filter(
        status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': Order.STATUS_CHOICES,
        'total_orders': total_orders,
        'pending_orders': pending_count,
        'today_orders': today_count,
        'total_revenue': revenue,
    }
    return render(request, 'admin_panel/orders.html', context)


# ADD THESE NEW VIEWS
@staff_required
def admin_order_detail(request, order_number):
    """Admin - Order Detail"""
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.order_number} updated to {order.get_status_display()}.')
            return redirect('admin_panel:order_detail', order_number=order_number)
    
    return render(request, 'admin_panel/order_detail.html', {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    })


@staff_required
def admin_orders_bulk_action(request):
    """Bulk update order status"""
    if request.method == 'POST':
        order_ids = request.POST.getlist('order_ids')
        new_status = request.POST.get('status')
        
        if order_ids and new_status in dict(Order.STATUS_CHOICES):
            updated = Order.objects.filter(id__in=order_ids).update(status=new_status)
            messages.success(request, f'{updated} orders updated.')
    
    return redirect('admin_panel:orders')