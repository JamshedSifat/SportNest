# payments/urls.py

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment Page
    path('<str:order_number>/', views.payment_page, name='payment_page'),
    
    # Process Payment
    path('<str:order_number>/process/', views.process_payment, name='process_payment'),
    
    # Admin Verify Payment
    path('<str:order_number>/verify/', views.payment_verification, name='payment_verification'),
    
    # Payment History
    path('history/', views.payment_history, name='payment_history'),
    
    # PDF Receipt
    path('receipt/<int:payment_id>/', views.payment_receipt, name='payment_receipt'),
    
    # Refund
    path('refund/<int:payment_id>/', views.request_refund, name='request_refund'),
    path('refund/<int:payment_id>/process/', views.process_refund, name='process_refund'),
    
    # Stripe
    path('<str:order_number>/stripe-intent/', views.create_stripe_payment_intent, name='stripe_intent'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
]