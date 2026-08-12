from django.contrib import admin
from .models import Cart, CartItem, Coupon

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('total_price',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'total_items', 'subtotal', 'total', 'updated_at')
    inlines = [CartItemInline]
    readonly_fields = ('total_items', 'subtotal', 'total')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'minimum_purchase', 'is_active', 'is_valid', 'used_count', 'valid_from', 'valid_to')
    list_filter = ('is_active',)
    search_fields = ('code',)
    list_editable = ('is_active',)