from .models import Cart


class CartSessionMixin:
	def get_cart(self):
		request = self.request

		if request.user.is_authenticated:
			cart, _ = Cart.objects.get_or_create(user=request.user)
		else:
			if not request.session.session_key:
				request.session.create()
			cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)

		return cart

	def get_or_create_cart(self):
		return self.get_cart()
