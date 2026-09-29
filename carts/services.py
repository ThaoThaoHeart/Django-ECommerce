from collections import Counter

from django.db import transaction

from catalog.models import Product
from .models import Cart, Order, OrderItem


def get_cart(request, create=True):
	"""Return the user's cart, or the session's cart for anonymous visitors."""
	if request.user.is_authenticated:
		if create:
			return Cart.objects.get_or_create(user=request.user)[0]
		return Cart.objects.filter(user=request.user).first()

	if not request.session.session_key:
		if not create:
			return None
		request.session.create()
	if create:
		return Cart.objects.get_or_create(session_key=request.session.session_key, user=None)[0]
	return Cart.objects.filter(session_key=request.session.session_key, user=None).first()


def merge_session_cart(request, user):
	"""Fold the anonymous cart into the user's cart. Call before login() rotates the session key."""
	session_cart = get_cart(request, create=False)
	if session_cart:
		Cart.objects.get_or_create(user=user)[0].merge(session_cart)


class CheckoutError(Exception):
	pass


@transaction.atomic
def place_order(user, cart, checkout):
	"""Turn the cart into an Order using validated checkout data, decrementing stock.

	Raises CheckoutError if the cart is empty or stock ran out.
	"""
	summary = cart.summary(checkout["province"])
	if not summary["items"] or summary["has_errors"]:
		raise CheckoutError("Some items in your cart are unavailable. Please review your cart.")

	quantities = Counter()
	for item in summary["items"]:
		quantities[item.product.pk] += item.quantity

	products = Product.objects.select_for_update().in_bulk(quantities)
	for product_id, quantity in quantities.items():
		product = products[product_id]
		if product.stock < quantity:
			raise CheckoutError(f"Sorry, only {product.stock} of {product.name} left in stock.")
		product.stock -= quantity
		product.save(update_fields=["stock"])

	payment = checkout["payment"]
	order = Order.objects.create(
		user=user,
		province=checkout["province"],
		billing_address=checkout["billing"],
		shipping_address=checkout["shipping"],
		cardholder_name=payment["cardholder_name"],
		card_last4=payment["card_number"][-4:],
		subtotal=summary["subtotal"],
		tax=summary["tax"],
		shipping_cost=summary["shipping_cost"],
		total=summary["total"],
	)
	OrderItem.objects.bulk_create(
		OrderItem(
			order=order,
			product_title=item.product_title,
			selected_variations=item.selected_variations,
			unit_price=item.unit_price,
			quantity=item.quantity,
		)
		for item in summary["items"]
	)
	cart.items.all().delete()
	return order
