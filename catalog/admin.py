from django.contrib import admin
from .models import Category, Product, Variation


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_in_stock', 'created_at']
    list_filter = ['created_at', 'stock', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ['product','variation_category', 'variation_value', 'is_active']
    list_editable = ('is_active',)
    