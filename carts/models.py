from decimal import Decimal

from django.conf import settings
from django.db import models

from catalog.models import Product
from .constants import CENT, PROVINCE_CHOICES, PROVINCES


class Cart(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
	session_key = models.CharField(max_length=40, null=True, blank=True)

	def add(self, product_title, selected_variations, quantity, max_quantity=None):
		item, _ = self.items.get_or_create(
			product_title=product_title,
			selected_variations=selected_variations,
			defaults={"quantity": 0},
		)
		item.quantity += quantity
		if max_quantity is not None:
			item.quantity = min(item.quantity, max_quantity)
		item.save(update_fields=["quantity"])
		return item

	def merge(self, other):
		for item in other.items.all():
			self.add(item.product_title, item.selected_variations, item.quantity)
		other.delete()

	def summary(self, province=None):
		"""Price every line against the live catalog and compute order totals.

		Lines whose product is gone or short on stock get an `error` message and block checkout.
		"""
		items = list(self.items.order_by("pk"))
		products = Product.objects.active().filter(name__in=[item.product_title for item in items])
		products_by_name = {product.name: product for product in products}

		for item in items:
			item.product = products_by_name.get(item.product_title)
			item.unit_price = item.product.price if item.product else Decimal("0.00")
			item.line_total = item.unit_price * item.quantity
			if not item.product or not item.product.is_in_stock():
				item.error = "This product is no longer available."
			elif item.quantity > item.product.stock:
				item.error = f"Only {item.product.stock} left in stock."
			else:
				item.error = ""

		subtotal = sum((item.line_total for item in items), Decimal("0.00"))
		_, tax_rate, shipping_cost = PROVINCES.get(province, (None, Decimal("0"), Decimal("0.00")))
		tax = (subtotal * tax_rate).quantize(CENT)
		return {
			"items": items,
			"item_count": sum(item.quantity for item in items),
			"has_errors": any(item.error for item in items),
			"province": province,
			"subtotal": subtotal,
			"tax": tax,
			"shipping_cost": shipping_cost,
			"total": subtotal + tax + shipping_cost,
		}


class CartItem(models.Model):
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
	product_title = models.CharField(max_length=250)
	selected_variations = models.CharField(max_length=500, blank=True, default="")
	quantity = models.PositiveIntegerField(default=1)

	def __str__(self):
		return f"{self.quantity} x {self.product_title}"


class Order(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
	created_at = models.DateTimeField(auto_now_add=True)
	province = models.CharField(max_length=2, choices=PROVINCE_CHOICES)
	billing_address = models.JSONField()
	shipping_address = models.JSONField()
	cardholder_name = models.CharField(max_length=200)
	card_last4 = models.CharField(max_length=4)
	subtotal = models.DecimalField(max_digits=10, decimal_places=2)
	tax = models.DecimalField(max_digits=10, decimal_places=2)
	shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
	total = models.DecimalField(max_digits=10, decimal_places=2)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"Order #{self.number}"

	@property
	def number(self):
		return f"{self.pk:06d}"

	def item_count(self):
		return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
	product_title = models.CharField(max_length=250)
	selected_variations = models.CharField(max_length=500, blank=True, default="")
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)
	quantity = models.PositiveIntegerField()

	@property
	def line_total(self):
		return self.unit_price * self.quantity
