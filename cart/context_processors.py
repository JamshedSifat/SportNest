# cart/context_processors.py

from .models import Cart

def cart_context(request):
    """Make cart data available globally"""
    cart_count = 0
    cart_total = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.total_items
            cart_total = cart.total
        except Cart.DoesNotExist:
            pass
    else:
        # Guest user - session based
        session_id = request.session.session_key
        if session_id:
            try:
                cart = Cart.objects.get(session_id=session_id)
                cart_count = cart.total_items
                cart_total = cart.total
            except Cart.DoesNotExist:
                pass
    
    return {
        'cart_count': cart_count,
        'cart_total': cart_total,
    }