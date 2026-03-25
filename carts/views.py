from django.shortcuts import redirect
from django.views.generic import DeleteView, RedirectView, TemplateView, UpdateView
from django.urls import reverse_lazy
from .mixins import CartSessionMixin
from .models import CartItem
from catalog.models import Product


class CartDetailView(CartSessionMixin, TemplateView):
	template_name = "carts/cart_detail.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		cart_items = []
		quantity = 0

		cart = self.get_cart()
		if cart is not None:
			cart_items = list(CartItem.objects.filter(cart=cart))
			product_titles = [item.product_title for item in cart_items]
			products = Product.objects.filter(name__in=product_titles)
			product_prices = {}

			for product in products:
				product_prices[product.name] = product.price
				
			for item in cart_items:
				quantity += item.quantity
				item.price = product_prices.get(item.product_title)
				item.line_total = item.price * item.quantity if item.price is not None else None
		
		total = sum(item.line_total for item in cart_items if item.line_total is not None)

		context.update(
			{	
				"cart_items": cart_items,
				"quantity": quantity,
				"total": total,
			}
		)
		return context


class CartRemoveView(CartSessionMixin, RedirectView):
	pattern_name = "carts:cart_detail"

	def get_redirect_url(self, *args, **kwargs):
		item_id = kwargs["item_id"]
		cart = self.get_cart()
		if cart is not None:
			try:
				cart_item = CartItem.objects.get(id=item_id, cart=cart)
				if cart_item.quantity > 1:
					cart_item.quantity -= 1
					cart_item.save()
				else:
					cart_item.delete()
			except CartItem.DoesNotExist:
				pass

		return super().get_redirect_url(*args, **kwargs)


class CartUpdateView(CartSessionMixin, UpdateView):
	model = CartItem
	fields = ["quantity"]
	pk_url_kwarg = "item_id"
	success_url = reverse_lazy("carts:cart_detail")

	def get_queryset(self):
		cart = self.get_cart()
		if cart is None:
			return CartItem.objects.none()
		return CartItem.objects.filter(cart=cart)

	def get(self, request, *args, **kwargs):
		return redirect("carts:cart_detail")

	def form_valid(self, form):
		raw_quantity = form.cleaned_data.get("quantity", 1)
		try:
			form.instance.quantity = max(1, int(raw_quantity))
		except (TypeError, ValueError):
			form.instance.quantity = 1
		return super().form_valid(form)

	def form_invalid(self, form):
		return redirect("carts:cart_detail")


class CartRemoveItemView(CartSessionMixin, DeleteView):
	model = CartItem
	pk_url_kwarg = "item_id"
	success_url = reverse_lazy("carts:cart_detail")

	def get_queryset(self):
		cart = self.get_cart()
		if cart is None:
			return CartItem.objects.none()
		return CartItem.objects.filter(cart=cart)

	def get(self, request, *args, **kwargs):
		return redirect("carts:cart_detail")
