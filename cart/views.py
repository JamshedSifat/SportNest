from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem, Coupon
from shop.models import Product
import json


def get_cart(request):
    """Get or create cart for user/session"""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_id=session_id)
    return cart


def cart_detail(request):
    """View cart details"""
    cart = get_cart(request)
    cart_items = cart.items.select_related(
        'product', 'product__brand', 'product__subcategory__main_category'
    ).all()

    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart/cart_detail.html', context)


# cart/views.py - UPDATE add_to_cart function

@require_POST
def add_to_cart(request, product_id):
    """Add product to cart (AJAX ready)"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_cart(request)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if product.stock <= 0:
        if is_ajax:
            return JsonResponse({'success': False, 'message': f'{product.name} is out of stock.'})
        messages.error(request, f'{product.name} is out of stock.')
        return redirect('shop:product_detail', slug=product.slug)

    if quantity > product.stock:
        quantity = product.stock

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        if cart_item.quantity > product.stock:
            cart_item.quantity = product.stock
        cart_item.save()

    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart!',
            'cart_count': cart.total_items,
            'cart_total': float(cart.total),
        })

    messages.success(request, f'✅ {product.name} added to cart!')
    return redirect('cart:cart_detail')

@require_POST
def update_cart(request, item_id):
    """Update cart item quantity (AJAX)"""
    cart = get_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if quantity > cart_item.product.stock:
        quantity = cart_item.product.stock

    if quantity < 1:
        cart_item.delete()
        if is_ajax:
            return JsonResponse({
                'success': True,
                'removed': True,
                'message': 'Item removed.',
                'cart_count': cart.total_items,
                'cart_total': float(cart.total),
                'subtotal': float(cart.subtotal),
            })
        messages.success(request, 'Item removed from cart.')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        if is_ajax:
            return JsonResponse({
                'success': True,
                'removed': False,
                'quantity': cart_item.quantity,
                'item_total': float(cart_item.total_price),
                'cart_count': cart.total_items,
                'cart_total': float(cart.total),
                'subtotal': float(cart.subtotal),
                'message': 'Cart updated!',
            })
        messages.success(request, 'Cart updated!')

    if not is_ajax:
        return redirect('cart:cart_detail')


@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart (AJAX)"""
    cart = get_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': f'{product_name} removed.',
            'cart_count': cart.total_items,
            'cart_total': float(cart.total),
            'subtotal': float(cart.subtotal),
        })

    messages.success(request, f'❌ {product_name} removed from cart.')
    return redirect('cart:cart_detail')


@require_POST
def clear_cart(request):
    """Clear cart"""
    cart = get_cart(request)
    cart.items.all().delete()

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        return JsonResponse({'success': True, 'message': 'Cart cleared!'})

    messages.success(request, 'Cart cleared!')
    return redirect('cart:cart_detail')


@require_POST
def apply_coupon(request):
    """Apply coupon code (AJAX)"""
    cart = get_cart(request)
    
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip().upper()
    except json.JSONDecodeError:
        code = request.POST.get('code', '').strip().upper()

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if not code:
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Please enter a coupon code.'})
        messages.error(request, 'Please enter a coupon code.')
        return redirect('cart:cart_detail')

    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
        
        # Check validity
        if not coupon.is_valid():
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'Coupon has expired or is not valid.'})
            messages.error(request, 'Coupon has expired.')
            return redirect('cart:cart_detail')

        # Check minimum purchase
        if cart.subtotal < coupon.minimum_purchase:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Minimum purchase of ৳{coupon.minimum_purchase} required.'
                })
            messages.error(request, f'Minimum purchase of ৳{coupon.minimum_purchase} required.')
            return redirect('cart:cart_detail')

        # Apply coupon
        cart.coupon = coupon
        cart.save()

        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'Coupon {code} applied! You saved ৳{coupon.discount_amount}!',
                'discount': float(coupon.discount_amount),
                'cart_total': float(cart.total),
                'subtotal': float(cart.subtotal),
            })

        messages.success(request, f'Coupon {code} applied! You saved ৳{coupon.discount_amount}!')

    except Coupon.DoesNotExist:
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Invalid coupon code.'})
        messages.error(request, 'Invalid coupon code.')

    if not is_ajax:
        return redirect('cart:cart_detail')


@require_POST
def remove_coupon(request):
    """Remove coupon from cart"""
    cart = get_cart(request)
    cart.coupon = None
    cart.save()

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': 'Coupon removed.',
            'cart_total': float(cart.total),
            'subtotal': float(cart.subtotal),
        })

    messages.success(request, 'Coupon removed.')
    return redirect('cart:cart_detail')