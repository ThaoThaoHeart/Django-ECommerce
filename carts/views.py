from django.shortcuts import redirect
from django.views.generic import DeleteView, RedirectView, TemplateView, UpdateView
from django.urls import reverse_lazy
from .mixins import CartSessionMixin
from .models import Cart, CartItem


class CartDetailView(CartSessionMixin, TemplateView):
	template_name = "carts/cart_detail.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		cart_items = []
		total = 0
		quantity = 0

		try:
			cart = self.get_cart()
			cart_items = CartItem.objects.filter(cart=cart).select_related("product").prefetch_related("variations")

			for item in cart_items:
				item.sub_total = item.product.price * item.quantity
				total += item.sub_total
				quantity += item.quantity
		except Cart.DoesNotExist:
			pass

		context.update(
			{
				"cart_items": cart_items,
				"total": total,
				"quantity": quantity,
			}
		)
		return context


class CartRemoveView(CartSessionMixin, RedirectView):
	pattern_name = "carts:cart_detail"

	def get_redirect_url(self, *args, **kwargs):
		item_id = kwargs["item_id"]
		try:
			cart = self.get_cart()
			cart_item = CartItem.objects.select_related("product").get(id=item_id, cart=cart)

			if cart_item.quantity > 1:
				cart_item.quantity -= 1
				cart_item.save()
			else:
				cart_item.delete()
		except (Cart.DoesNotExist, CartItem.DoesNotExist):
			pass

		return super().get_redirect_url(*args, **kwargs)


class CartUpdateView(CartSessionMixin, UpdateView):
	model = CartItem
	fields = ["quantity"]
	pk_url_kwarg = "item_id"
	success_url = reverse_lazy("carts:cart_detail")

	def get_queryset(self):
		try:
			cart = self.get_cart()
		except Cart.DoesNotExist:
			return CartItem.objects.none()
		return CartItem.objects.select_related("product").filter(cart=cart)

	def get(self, request, *args, **kwargs):
		return redirect("carts:cart_detail")

	def form_valid(self, form):
		product = form.instance.product
		raw_quantity = form.cleaned_data.get("quantity", 1)
		try:
			form.instance.quantity = min(max(1, int(raw_quantity)), product.stock)
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
		try:
			cart = self.get_cart()
		except (Cart.DoesNotExist, CartItem.DoesNotExist):
			return CartItem.objects.none()
		return CartItem.objects.filter(cart=cart)

	def get(self, request, *args, **kwargs):
		return redirect("carts:cart_detail")
