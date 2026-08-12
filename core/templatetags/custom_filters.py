from django import template
from django.utils.html import format_html

register = template.Library()

@register.filter(name='currency')
def currency(value):
    """Format number as Bangladeshi Taka - ৳1,500"""
    try:
        value = int(value)
        return f'৳{value:,}'
    except (ValueError, TypeError):
        return f'৳{value}'

@register.filter(name='stars')
def stars(rating):
    """Convert 4.5 to ★★★★½"""
    try:
        rating = float(rating)
        full = int(rating)
        half = rating - full >= 0.5
        empty = 5 - full - (1 if half else 0)
        return '★' * full + ('½' if half else '') + '☆' * empty
    except:
        return '☆☆☆☆☆'

@register.filter(name='truncate')
def truncate(value, length=100):
    """Truncate text with ..."""
    if len(str(value)) > length:
        return str(value)[:length] + '...'
    return value