from .models import Cart

def cart_context(request):
    """Make cart data globally available (user + guest)"""
    cart_count = 0
    cart_total = 0

    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            cart = Cart.objects.filter(session_id=session_id).first()

        if cart:
            cart_count = cart.total_items
            cart_total = cart.total
    except Exception:
        pass

    return {
        'cart_count': cart_count,
        'cart_total': cart_total,
    }