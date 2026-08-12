from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import MainCategory, SubCategory, Product


def _get_cart(request):
    return request.session.get('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def shop_home(request):
    """Shop main page - Show all categories"""
    main_categories = MainCategory.objects.filter(is_active=True).order_by('order', 'name')

    context = {
        'main_categories': main_categories,
    }
    return render(request, 'shop/shop_home.html', context)


def category_detail(request, slug):
    """Show subcategories of a main category"""
    category = get_object_or_404(MainCategory, slug=slug, is_active=True)
    subcategories = category.subcategories.filter(is_active=True).order_by('order', 'name')

    context = {
        'category': category,
        'subcategories': subcategories,
    }
    return render(request, 'shop/category_detail.html', context)


def subcategory_detail(request, slug):
    """Show products of a subcategory with filter/sort/search"""
    subcategory = get_object_or_404(SubCategory, slug=slug, is_active=True)
    products_qs = subcategory.products.filter(is_active=True).select_related('brand')

    # query params
    q = request.GET.get('q', '').strip()
    brand = request.GET.get('brand', '').strip()
    stock = request.GET.get('stock', '').strip()  # in/out
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    sort = request.GET.get('sort', 'newest').strip()

    if q:
        products_qs = products_qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(brand__name__icontains=q)
        )

    if brand:
        products_qs = products_qs.filter(brand__slug=brand)

    if stock == 'in':
        products_qs = products_qs.filter(stock__gt=0)
    elif stock == 'out':
        products_qs = products_qs.filter(stock__lte=0)

    if min_price:
        try:
            products_qs = products_qs.filter(price__gte=min_price)
        except Exception:
            pass

    if max_price:
        try:
            products_qs = products_qs.filter(price__lte=max_price)
        except Exception:
            pass

    sort_map = {
        'newest': '-created_at',
        'price_asc': 'price',
        'price_desc': '-price',
        'name_asc': 'name',
        'name_desc': '-name',
    }
    products_qs = products_qs.order_by(sort_map.get(sort, '-created_at'))

    paginator = Paginator(products_qs, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    # brands for filter dropdown
    brands = subcategory.products.filter(
        is_active=True, brand__isnull=False
    ).select_related('brand').values_list('brand__name', 'brand__slug').distinct()

    context = {
        'subcategory': subcategory,
        'products': products,
        'brands': brands,
        'filters': {
            'q': q,
            'brand': brand,
            'stock': stock,
            'min_price': min_price,
            'max_price': max_price,
            'sort': sort,
        }
    }
    return render(request, 'shop/subcategory_detail.html', context)


def product_detail(request, slug):
    """Product detail page"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        subcategory=product.subcategory,
        is_active=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'shop/product_detail.html', context)


def add_to_cart(request, slug):
    if request.method != 'POST':
        return redirect('shop:product_detail', slug=slug)

    product = get_object_or_404(Product, slug=slug, is_active=True)
    qty = request.POST.get('quantity', 1)

    try:
        qty = int(qty)
    except ValueError:
        qty = 1

    if qty < 1:
        qty = 1

    if product.stock <= 0:
        return redirect('shop:product_detail', slug=slug)

    qty = min(qty, product.stock)

    cart = _get_cart(request)
    current = int(cart.get(str(product.id), 0))
    new_qty = min(current + qty, product.stock)
    cart[str(product.id)] = new_qty
    _save_cart(request, cart)

    return redirect('shop:product_detail', slug=slug)


def cart_detail(request):
    cart = _get_cart(request)
    product_ids = [int(pid) for pid in cart.keys()] if cart else []
    products = Product.objects.filter(id__in=product_ids, is_active=True)

    items = []
    total = 0
    for p in products:
        qty = int(cart.get(str(p.id), 0))
        subtotal = p.price * qty
        total += subtotal
        items.append({
            'product': p,
            'quantity': qty,
            'subtotal': subtotal,
        })

    return render(request, 'shop/cart_detail.html', {'items': items, 'total': total})


def cart_update(request, slug):
    if request.method != 'POST':
        return redirect('shop:cart_detail')

    product = get_object_or_404(Product, slug=slug, is_active=True)
    qty = request.POST.get('quantity', 1)

    try:
        qty = int(qty)
    except ValueError:
        qty = 1

    cart = _get_cart(request)

    if qty <= 0:
        cart.pop(str(product.id), None)
    else:
        cart[str(product.id)] = min(qty, max(product.stock, 0))

    _save_cart(request, cart)
    return redirect('shop:cart_detail')


def cart_remove(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    cart = _get_cart(request)
    cart.pop(str(product.id), None)
    _save_cart(request, cart)
    return redirect('shop:cart_detail')

def all_products(request):
    """Show all products across all categories"""
    products_qs = Product.objects.filter(is_active=True).select_related(
        'brand', 'subcategory__main_category'
    ).order_by('-created_at')
    
    q = request.GET.get('q', '').strip()
    if q:
        products_qs = products_qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(brand__name__icontains=q)
        )
    
    sort = request.GET.get('sort', 'newest').strip()
    sort_map = {
        'newest': '-created_at',
        'price_asc': 'price',
        'price_desc': '-price',
        'name_asc': 'name',
    }
    products_qs = products_qs.order_by(sort_map.get(sort, '-created_at'))
    
    paginator = Paginator(products_qs, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'q': q,
        'sort': sort,
    }
    return render(request, 'shop/all_products.html', context)