from .models import Cart


class CartSessionMixin:
	def get_cart_id(self):
		cart = self.request.session.session_key
		if not cart:
			self.request.session.create()
			cart = self.request.session.session_key
		return cart

	def get_cart(self):
		return Cart.objects.get(cart_id=self.get_cart_id())

	def get_or_create_cart(self):
		cart, _ = Cart.objects.get_or_create(cart_id=self.get_cart_id())
		return cart