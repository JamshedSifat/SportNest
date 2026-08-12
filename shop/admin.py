from django.contrib import admin
from django.utils.html import format_html
from .models import MainCategory, SubCategory, Brand, Product, ProductImage

class SubCategoryInline(admin.TabularInline):
    """Show subcategories inside main category"""
    model = SubCategory
    extra = 1
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'subcategory_count', 'product_count', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SubCategoryInline]
    list_editable = ('order', 'is_active')


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_category', 'product_count', 'is_active')
    list_filter = ('main_category', 'is_active')
    search_fields = ('name', 'main_category__name')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'subcategory', 'brand', 'price', 'stock', 'is_in_stock', 'is_active')
    list_filter = ('subcategory__main_category', 'subcategory', 'brand', 'is_active')
    search_fields = ('name', 'sku', 'subcategory__name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    list_editable = ('stock', 'is_active')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}