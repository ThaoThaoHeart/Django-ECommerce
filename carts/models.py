from django.db import models


class Cart(models.Model):
	user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, null=True, blank=True)
	session_key = models.CharField(max_length=40, null=True, blank=True)

	def cart_count(self):
		count = self.items.count()
		return count if count > 0 else 0
        
class CartItem(models.Model):
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
	product_title = models.CharField(max_length=250)
	selected_variations = models.CharField(max_length=500, blank=True, default="")
	quantity = models.PositiveIntegerField(default=1)
