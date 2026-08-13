# payments/models.py

from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order

User = get_user_model()


class Payment(models.Model):
    """Payment Model"""
    
    PAYMENT_METHODS = [
        ('COD', 'Cash on Delivery'),
        ('BKASH', 'bKash'),
        ('NAGAD', 'Nagad'),
        ('ROCKET', 'Rocket'),
        ('CARD', 'Credit/Debit Card'),
        ('STRIPE', 'Stripe'),
    ]
    
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Basic Info
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Payment Details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='COD')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    
    # Amount
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    
    # Mobile Banking Fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    sender_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Card Fields (if needed)
    card_last_four = models.CharField(max_length=4, blank=True, null=True)
    card_brand = models.CharField(max_length=50, blank=True, null=True)
    
    # Stripe Fields
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Notes
    admin_notes = models.TextField(blank=True, null=True)
    customer_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True) 
     # Refund Fields
    refund_requested = models.BooleanField(default=False)
    refund_reason = models.TextField(blank=True, null=True)
    refund_status = models.CharField(max_length=20, blank=True, null=True, 
                                      choices=[('REQUESTED', 'Requested'), 
                                               ('APPROVED', 'Approved'), 
                                               ('REJECTED', 'Rejected')])
    refund_processed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment #{self.id} - {self.order.order_number} - {self.get_payment_status_display()}"
    
    def mark_as_paid(self, transaction_id=None):
        """Mark payment as completed"""
        self.payment_status = 'COMPLETED'
        if transaction_id:
            self.transaction_id = transaction_id
        self.paid_at = timezone.now()
        self.save()
        
        # Update order status
        self.order.status = 'CONFIRMED'
        self.order.save()
    
    def mark_as_failed(self):
        """Mark payment as failed"""
        self.payment_status = 'FAILED'
        self.save()


class MobileBankingConfig(models.Model):
    """Mobile Banking Configuration"""
    
    PROVIDERS = [
        ('BKASH', 'bKash'),
        ('NAGAD', 'Nagad'),
        ('ROCKET', 'Rocket'),
    ]
    
    provider = models.CharField(max_length=20, choices=PROVIDERS, unique=True)
    account_number = models.CharField(max_length=20)
    account_type = models.CharField(max_length=20, default='Merchant')
    is_active = models.BooleanField(default=True)
    instructions = models.TextField(blank=True, null=True)
    icon = models.ImageField(upload_to='payments/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_provider_display()} - {self.account_number}"