from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from cart.models import Cart
from .models import Order, OrderItem


@login_required
def checkout(request):
    """Checkout page"""
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')
    
    if cart.total_items == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')
    
    cart_items = cart.items.select_related('product').all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def place_order(request):
    """Place order"""
    if request.method != 'POST':
        return redirect('cart:cart_detail')
    
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')
    
    if cart.total_items == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')
    
    # Get form data
    full_name = request.POST.get('full_name', request.user.get_full_name())
    phone = request.POST.get('phone', request.user.phone or '')
    email = request.POST.get('email', request.user.email)
    address = request.POST.get('address', request.user.address or '')
    city = request.POST.get('city', request.user.city or 'Dhaka')
    postal_code = request.POST.get('postal_code', '')
    payment_method = request.POST.get('payment_method', 'COD')
    notes = request.POST.get('notes', '')
    
    # Validate
    if not all([full_name, phone, email, address, city]):
        messages.error(request, 'Please fill all required fields.')
        return redirect('orders:checkout')
    
    # Create order
    order = Order.objects.create(
        user=request.user,
        email=email,
        phone=phone,
        full_name=full_name,
        address=address,
        city=city,
        postal_code=postal_code,
        payment_method=payment_method,
        notes=notes,
        subtotal=cart.subtotal,
        discount=cart.discount,
        total=cart.total,
    )
    
    # Create order items
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            price=item.product.price,
            quantity=item.quantity,
            subtotal=item.total_price,
        )
        
        # Update stock
        item.product.stock -= item.quantity
        if item.product.stock < 0:
            item.product.stock = 0
        item.product.save()
    
    # Update coupon usage
    if cart.coupon:
        cart.coupon.used_count += 1
        cart.coupon.save()
    
    # Clear cart
    cart.items.all().delete()
    cart.coupon = None
    cart.save()
    
    messages.success(request, f'✅ Order #{order.order_number} placed successfully!')
    return redirect('orders:order_confirmation', order_number=order.order_number)


def order_confirmation(request, order_number):
    """Order confirmation page"""
    from django.shortcuts import get_object_or_404
    
    if request.user.is_authenticated:
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
    else:
        order = get_object_or_404(Order, order_number=order_number)
    
    return render(request, 'orders/order_confirmation.html', {'order': order})


@login_required
def my_orders(request):
    """User's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    """Order detail"""
    from django.shortcuts import get_object_or_404
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})