from decimal import Decimal
from django.db import models


PROVINCE_TAX_RATES = {
	"ON": Decimal("0.13"),
	"BC": Decimal("0.12"),
	"AB": Decimal("0.05"),
	"QC": Decimal("0.14975"),
	"MB": Decimal("0.12"),
	"SK": Decimal("0.11"),
	"NS": Decimal("0.15"),
	"NB": Decimal("0.15"),
	"NL": Decimal("0.15"),
	"PE": Decimal("0.15"),
}

PROVINCE_SHIPPING_COSTS = {
	"ON": Decimal("0.00"),
	"BC": Decimal("12.00"),
	"AB": Decimal("10.00"),
	"QC": Decimal("9.00"),
	"MB": Decimal("11.00"),
	"SK": Decimal("11.00"),
	"NS": Decimal("14.00"),
	"NB": Decimal("14.00"),
	"NL": Decimal("16.00"),
	"PE": Decimal("14.00"),
}


class Cart(models.Model):
	user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, null=True, blank=True)
	session_key = models.CharField(max_length=40, null=True, blank=True)

	def cart_count(self):
		count = self.items.count()
		return count if count > 0 else 0

	def priced_items(self):
		from catalog.models import Product

		cart_items = list(self.items.all())
		if not cart_items:
			return cart_items

		product_titles = [item.product_title for item in cart_items]
		products = Product.objects.filter(name__in=product_titles)
		product_prices = {product.name: product.price for product in products}

		for item in cart_items:
			item.price = product_prices.get(item.product_title, Decimal("0.00"))
			item.line_total = item.price * item.quantity

		return cart_items

	def snapshot(self):
		cart_items = self.priced_items()
		quantity = sum((item.quantity for item in cart_items), 0)
		subtotal = sum((item.line_total for item in cart_items), Decimal("0.00"))
		return cart_items, quantity, subtotal

	@staticmethod
	def tax_shipping_total(subtotal, province_code):
		rate = PROVINCE_TAX_RATES.get(province_code, Decimal("0.00"))
		tax_amount = (subtotal * rate).quantize(Decimal("0.01"))
		shipping_cost = PROVINCE_SHIPPING_COSTS.get(province_code, Decimal("0.00")).quantize(Decimal("0.01"))
		grand_total = (subtotal + tax_amount + shipping_cost).quantize(Decimal("0.01"))
		return tax_amount, shipping_cost, grand_total

	def decrement_or_remove_item(self, item_id):
		try:
			cart_item = self.items.get(id=item_id)
		except CartItem.DoesNotExist:
			return

		if cart_item.quantity > 1:
			cart_item.quantity -= 1
			cart_item.save(update_fields=["quantity"])
		else:
			cart_item.delete()

	def clear_items(self):
		self.items.all().delete()
        
class CartItem(models.Model):
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
	product_title = models.CharField(max_length=250)
	selected_variations = models.CharField(max_length=500, blank=True, default="")
	quantity = models.PositiveIntegerField(default=1)
