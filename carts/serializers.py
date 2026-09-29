from rest_framework import serializers

from catalog.serializers import ProductSerializer
from .constants import PROVINCES
from .models import Order, OrderItem


class CartLineSerializer(serializers.Serializer):
	id = serializers.IntegerField()
	product_title = serializers.CharField()
	selected_variations = serializers.CharField()
	quantity = serializers.IntegerField()
	unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
	line_total = serializers.DecimalField(max_digits=10, decimal_places=2)
	error = serializers.CharField()
	product = ProductSerializer(allow_null=True)


class CartSummarySerializer(serializers.Serializer):
	items = CartLineSerializer(many=True)
	item_count = serializers.IntegerField()
	has_errors = serializers.BooleanField()
	province = serializers.CharField(allow_null=True)
	subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
	tax = serializers.DecimalField(max_digits=10, decimal_places=2)
	shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
	total = serializers.DecimalField(max_digits=10, decimal_places=2)


class OrderItemSerializer(serializers.ModelSerializer):
	line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

	class Meta:
		model = OrderItem
		fields = ["id", "product_title", "selected_variations", "unit_price", "quantity", "line_total"]


class OrderSerializer(serializers.ModelSerializer):
	items = OrderItemSerializer(many=True, read_only=True)
	province_name = serializers.CharField(source="get_province_display", read_only=True)
	item_count = serializers.IntegerField(read_only=True)

	class Meta:
		model = Order
		fields = [
			"id", "number", "created_at", "province", "province_name", "billing_address", "shipping_address",
			"cardholder_name", "card_last4", "subtotal", "tax", "shipping_cost", "total", "item_count", "items",
		]


def province_list():
	return [{"code": code, "name": name, "tax_rate": rate, "shipping_cost": shipping} for code, (name, rate, shipping) in PROVINCES.items()]
