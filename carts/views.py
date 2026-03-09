from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Product

from .models import Cart, CartItem


def cart_id(request):
	cart = request.session.session_key
	if not cart:
		request.session.create()
	return cart


def cart_detail(request):
	cart_items = []
	total = 0
	quantity = 0

	try:
		cart = Cart.objects.get(cart_id=cart_id(request))
		cart_items = CartItem.objects.filter(cart=cart).select_related("product")

		for item in cart_items:
			item.sub_total = item.product.price * item.quantity
			total += item.sub_total
			quantity += item.quantity
	except Cart.DoesNotExist:
		pass

	context = {
		"cart_items": cart_items,
		"total": total,
		"quantity": quantity,
	}
	return render(request, "carts/cart_detail.html", context)


def cart_add(request, product_id):
	product = get_object_or_404(Product, id=product_id, is_active=True)

	quantity_to_add = 1
	if request.method == "POST":
		raw_quantity = request.POST.get("quantity", 1)
		quantity_to_add = max(1, int(raw_quantity))

	cart, _ = Cart.objects.get_or_create(cart_id=cart_id(request))
	cart_item, _ = CartItem.objects.get_or_create(
		product=product,
		cart=cart,
	)

	cart_item.quantity = min(cart_item.quantity + quantity_to_add, product.stock)

	if cart_item.quantity > 0:
		cart_item.save()
	else:
		cart_item.delete()

	return redirect("carts:cart_detail")


def cart_remove(request, product_id):
	product = get_object_or_404(Product, id=product_id)

	try:
		cart = Cart.objects.get(cart_id=cart_id(request))
		cart_item = CartItem.objects.get(product=product, cart=cart)

		if cart_item.quantity > 1:
			cart_item.quantity -= 1
			cart_item.save()
		else:
			cart_item.delete()
	except (Cart.DoesNotExist, CartItem.DoesNotExist):
		pass

	return redirect("carts:cart_detail")


def cart_update(request, product_id):
	if request.method != "POST":
		return redirect("carts:cart_detail")

	product = get_object_or_404(Product, id=product_id, is_active=True)
	raw_quantity = request.POST.get("quantity", 1)
	quantity = min(max(1, int(raw_quantity)), product.stock)

	try:
		cart = Cart.objects.get(cart_id=cart_id(request))
		cart_item = CartItem.objects.get(product=product, cart=cart)
		cart_item.quantity = quantity
		cart_item.save()
	except (Cart.DoesNotExist, CartItem.DoesNotExist):
		pass

	return redirect("carts:cart_detail")


def cart_remove_item(request, product_id):
	product = get_object_or_404(Product, id=product_id)

	try:
		cart = Cart.objects.get(cart_id=cart_id(request))
		cart_item = CartItem.objects.get(product=product, cart=cart)
		cart_item.delete()
	except (Cart.DoesNotExist, CartItem.DoesNotExist):
		pass

	return redirect("carts:cart_detail")
