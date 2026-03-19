from .models import Cart


class CartSessionMixin:
	cart_session_key = "cart_id"

	def get_session_cart_id(self):
		cart_id = self.request.session.get(self.cart_session_key)
		if cart_id:
			return cart_id

		if not self.request.session.session_key:
			self.request.session.create()

		cart_id = self.request.session.session_key
		self.request.session[self.cart_session_key] = cart_id
		return cart_id

	def get_cart(self):
		cart_id = self.get_session_cart_id()
		cart = Cart.objects.filter(cart_id=cart_id).order_by("id").first()
		if cart is None:
			raise Cart.DoesNotExist
		return cart

	def get_or_create_cart(self):
		cart_id = self.get_session_cart_id()
		cart = Cart.objects.filter(cart_id=cart_id).order_by("id").first()
		if cart:
			return cart
		return Cart.objects.create(cart_id=cart_id)