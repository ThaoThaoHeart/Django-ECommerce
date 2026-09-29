from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0
	readonly_fields = ["product_title", "selected_variations", "unit_price", "quantity"]
	can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ["__str__", "user", "created_at", "province", "total"]
	list_filter = ["province", "created_at"]
	search_fields = ["user__email"]
	readonly_fields = ["created_at"]
	inlines = [OrderItemInline]
