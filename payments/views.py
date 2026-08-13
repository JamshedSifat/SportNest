# payments/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from orders.models import Order
from .models import Payment, MobileBankingConfig
import stripe
import json
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test

def staff_required(view_func):
    """Decorator to check if user is staff"""
    decorated_view = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url='admin_panel:login'
    )
    return decorated_view(view_func)

@login_required
def payment_page(request, order_number):
    """Payment page after checkout"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Check if payment already exists
    if hasattr(order, 'payment'):
        if order.payment.payment_status == 'COMPLETED':
            messages.info(request, 'Payment already completed.')
            return redirect('orders:order_confirmation', order_number=order_number)
    
    # Get mobile banking configs
    banking_configs = MobileBankingConfig.objects.filter(is_active=True)
    
    context = {
        'order': order,
        'banking_configs': banking_configs,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY if hasattr(settings, 'STRIPE_PUBLIC_KEY') else '',
    }
    return render(request, 'payments/payment_page.html', context)


@login_required
@require_POST
def process_payment(request, order_number):
    """Process payment"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    payment_method = request.POST.get('payment_method', 'COD')
    
    # Create or get payment
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'user': request.user,
            'amount': order.total,
            'payment_method': payment_method,
        }
    )
    
    if payment_method == 'COD':
        # Cash on Delivery - no extra processing needed
        payment.payment_status = 'PENDING'
        payment.save()
        messages.success(request, '✅ Order placed successfully! Pay on delivery.')
        return redirect('orders:order_confirmation', order_number=order_number)
    
    elif payment_method in ['BKASH', 'NAGAD', 'ROCKET']:
        # Mobile Banking
        phone = request.POST.get('phone_number', '')
        transaction_id = request.POST.get('sender_transaction_id', '')
        
        if not phone or not transaction_id:
            messages.error(request, 'Please provide phone number and transaction ID.')
            return redirect('payments:payment_page', order_number=order_number)
        
        payment.phone_number = phone
        payment.sender_transaction_id = transaction_id
        payment.payment_status = 'PENDING'  # Admin will verify
        payment.save()
        
        messages.success(request, '✅ Payment information submitted! We will verify your payment shortly.')
        return redirect('orders:order_confirmation', order_number=order_number)
    
    elif payment_method == 'STRIPE':
        # Stripe payment - handle via AJAX on frontend
        return JsonResponse({'success': True, 'client_secret': 'stripe_client_secret_here'})
    
    messages.error(request, 'Invalid payment method.')
    return redirect('payments:payment_page', order_number=order_number)


@login_required
def payment_verification(request, order_number):
    """Verify mobile banking payment (for admin)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('admin_panel:dashboard')
    
    order = get_object_or_404(Order, order_number=order_number)
    payment = get_object_or_404(Payment, order=order)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'verify':
            payment.mark_as_paid(transaction_id=payment.sender_transaction_id)
            messages.success(request, f'Payment #{payment.id} verified successfully!')
        elif action == 'reject':
            payment.mark_as_failed()
            messages.warning(request, f'Payment #{payment.id} rejected.')
        
        return redirect('admin_panel:order_detail', order_number=order_number)
    
    return render(request, 'admin_panel/payment_verify.html', {
        'payment': payment,
        'order': order,
    })


@login_required
def payment_history(request):
    """User's payment history"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/payment_history.html', {'payments': payments})


# ============ STRIPE INTEGRATION ============
@login_required
@require_POST
def create_stripe_payment_intent(request, order_number):
    """Create Stripe Payment Intent"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(order.total * 100),  # Stripe uses cents
            currency='bdt',
            metadata={
                'order_number': order.order_number,
                'user_id': request.user.id,
            }
        )
        
        # Create payment record
        Payment.objects.create(
            order=order,
            user=request.user,
            amount=order.total,
            payment_method='STRIPE',
            payment_status='PENDING',
            stripe_payment_intent_id=intent.id,
        )
        
        return JsonResponse({
            'clientSecret': intent.client_secret
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def payment_receipt(request, payment_id):
    """Generate PDF receipt"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Create PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Header
    p.setFont("Helvetica-Bold", 24)
    p.drawString(50, 750, "SportNest")
    p.setFont("Helvetica", 12)
    p.drawString(50, 730, "Payment Receipt")
    p.line(50, 720, 550, 720)
    
    # Payment Details
    y = 690
    details = [
        f"Receipt #: RCP-{payment.id}",
        f"Order #: {payment.order.order_number}",
        f"Date: {payment.paid_at.strftime('%B %d, %Y') if payment.paid_at else 'Pending'}",
        f"Payment Method: {payment.get_payment_method_display()}",
        f"Amount: ৳{payment.amount}",
        f"Status: {payment.get_payment_status_display()}",
        f"Transaction ID: {payment.transaction_id or 'N/A'}",
    ]
    
    p.setFont("Helvetica", 12)
    for detail in details:
        p.drawString(50, y, detail)
        y -= 25
    
    # Footer
    p.setFont("Helvetica", 10)
    p.drawString(50, 100, "Thank you for shopping with SportNest!")
    p.drawString(50, 80, "For any queries, contact: support@sportnest.com")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt-{payment.id}.pdf"'
    return response


@login_required
@require_POST
def request_refund(request, payment_id):
    """Request refund"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if payment.payment_status != 'COMPLETED':
        messages.error(request, 'Only completed payments can be refunded.')
        return redirect('payments:payment_history')
    
    if payment.refund_requested:
        messages.warning(request, 'Refund already requested.')
        return redirect('payments:payment_history')
    
    reason = request.POST.get('reason', '')
    payment.refund_requested = True
    payment.refund_reason = reason
    payment.refund_status = 'REQUESTED'
    payment.save()
    
    # Notify admin
    send_refund_notification(payment)
    
    messages.success(request, 'Refund request submitted. We will review it shortly.')
    return redirect('payments:payment_history')


@staff_required
def process_refund(request, payment_id):
    """Admin: Process refund"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            payment.payment_status = 'REFUNDED'
            payment.refund_status = 'APPROVED'
            payment.order.status = 'REFUNDED'
            payment.order.save()
            payment.save()
            
            # Send email to customer
            send_refund_approved_email(payment)
            messages.success(request, 'Refund approved.')
            
        elif action == 'reject':
            payment.refund_status = 'REJECTED'
            payment.admin_notes = request.POST.get('notes', '')
            payment.save()
            messages.warning(request, 'Refund rejected.')
        
        return redirect('admin_panel:order_detail', order_number=payment.order.order_number)
    
    return render(request, 'admin_panel/refund_process.html', {'payment': payment})


def send_refund_notification(payment):
    """Send refund request notification to admin"""
    subject = f'Refund Request - Order #{payment.order.order_number}'
    message = f'''
    Refund Request Details:
    Order: #{payment.order.order_number}
    Customer: {payment.user.get_full_name()}
    Amount: ৳{payment.amount}
    Reason: {payment.refund_reason}
    
    Please review in admin panel.
    '''
    send_mail(
        subject, message, settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL], fail_silently=True
    )


def send_refund_approved_email(payment):
    """Send refund approved email to customer"""
    subject = f'Refund Approved - Order #{payment.order.order_number}'
    message = f'''
    Dear {payment.user.first_name},
    
    Your refund of ৳{payment.amount} for Order #{payment.order.order_number} has been approved.
    The amount will be credited to your original payment method within 5-10 business days.
    
    Thank you,
    SportNest Team
    '''
    send_mail(
        subject, message, settings.DEFAULT_FROM_EMAIL,
        [payment.user.email], fail_silently=True
    )

@require_POST
def stripe_webhook(request):
    """Stripe Webhook Handler"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle payment intent succeeded
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
            payment.mark_as_paid(transaction_id=payment_intent['id'])
        except Payment.DoesNotExist:
            pass
    
    return JsonResponse({'status': 'success'})