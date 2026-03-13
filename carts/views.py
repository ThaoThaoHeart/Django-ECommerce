from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, View, FormView
from django.urls import reverse_lazy
from catalog.models import Product
from .forms import CartAddForm
from .models import Cart, CartItem


class CartSessionMixin:
	def get_cart_id(self):
		cart = self.request.session.session_key
		if not cart:
			self.request.session.create()
			cart = self.request.session.session_key
		return cart

	def get_cart(self):
		return Cart.objects.get(cart_id=self.get_cart_id())


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


class CartAddView(CartSessionMixin, FormView):
	template_name = "carts/cart_detail.html"
	form_class = CartAddForm
	success_url = reverse_lazy("carts:cart_detail")

	def get_product(self):
		return get_object_or_404(Product, id=self.kwargs["product_id"], is_active=True)

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs["product"] = self.get_product()
		return kwargs

	def form_valid(self, form):
		product = self.get_product()
		quantity_to_add = form.cleaned_data["quantity"]
		selected_variations = form.cleaned_data.get("selected_variations", [])
		selected_variation_ids = {variation.id for variation in selected_variations}
		cart, _ = Cart.objects.get_or_create(cart_id=self.get_cart_id())

		cart_item = None
		existing_items = (
			CartItem.objects.filter(product=product, cart=cart)
			.prefetch_related("variations")
		)
		for item in existing_items:
			item_variation_ids = set(item.variations.values_list("id", flat=True))
			if item_variation_ids == selected_variation_ids:
				cart_item = item
				break

		if cart_item is None:
			cart_item = CartItem.objects.create(product=product, cart=cart, quantity=0)
			if selected_variations:
				cart_item.variations.set(selected_variations)

		cart_item.quantity = min(cart_item.quantity + quantity_to_add, product.stock)

		if cart_item.quantity > 0:
			cart_item.save()
		else:
			cart_item.delete()

		return super().form_valid(form)

	def form_invalid(self, form):
		return redirect("carts:cart_detail")


class CartRemoveView(CartSessionMixin, View):
	def get(self, request, item_id):
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

		return redirect("carts:cart_detail")


class CartUpdateView(CartSessionMixin, View):
	def post(self, request, item_id):
		try:
			cart = self.get_cart()
			cart_item = CartItem.objects.select_related("product").get(id=item_id, cart=cart)
		except (Cart.DoesNotExist, CartItem.DoesNotExist):
			return redirect("carts:cart_detail")

		product = cart_item.product
		raw_quantity = request.POST.get("quantity", 1)
		try:
			quantity = min(max(1, int(raw_quantity)), product.stock)
		except (TypeError, ValueError):
			quantity = 1

		cart_item.quantity = quantity
		cart_item.save()

		return redirect("carts:cart_detail")

	def get(self, request, item_id):
		return redirect("carts:cart_detail")


class CartRemoveItemView(CartSessionMixin, View):
	def get(self, request, item_id):
		try:
			cart = self.get_cart()
			cart_item = CartItem.objects.get(id=item_id, cart=cart)
			cart_item.delete()
		except (Cart.DoesNotExist, CartItem.DoesNotExist):
			pass

		return redirect("carts:cart_detail")
