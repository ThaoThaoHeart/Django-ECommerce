from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import Product
from djangoecommerce.api import form_errors
from .constants import PROVINCES
from .forms import CHECKOUT_SECTIONS, CartAddForm, validate_checkout
from .models import CartItem
from .serializers import CartSummarySerializer, OrderSerializer, province_list
from .services import CheckoutError, get_cart, place_order


def cart_response(request, status_code=status.HTTP_200_OK):
	province = request.query_params.get("province")
	summary = get_cart(request).summary(province if province in PROVINCES else None)
	return Response(CartSummarySerializer(summary, context={"request": request}).data, status=status_code)


class CartView(APIView):
	"""GET the priced cart; pass ?province=XX to include tax and shipping."""

	def get(self, request):
		return cart_response(request)


class CartItemListView(APIView):
	"""POST {product: <slug>, quantity, variations: {<category>: <variation id>}} to add a line."""

	def post(self, request):
		product = get_object_or_404(Product.objects.active(), slug=request.data.get("product"))
		variations = request.data.get("variations") or {}
		data = {"quantity": request.data.get("quantity", 1), **{f"variation_{key}": value for key, value in variations.items()}}
		form = CartAddForm(data, product=product)
		if not form.is_valid():
			return Response({"errors": form_errors(form)}, status=status.HTTP_400_BAD_REQUEST)

		get_cart(request).add(product.name, form.selected_variations(), form.cleaned_data["quantity"], max_quantity=product.stock)
		return cart_response(request, status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
	"""PATCH {quantity} to change a line (capped at stock), DELETE to remove it."""

	def get_item(self, request, item_id):
		return get_object_or_404(CartItem, pk=item_id, cart=get_cart(request))

	def patch(self, request, item_id):
		item = self.get_item(request, item_id)
		try:
			quantity = int(request.data.get("quantity"))
		except (TypeError, ValueError):
			return Response({"errors": {"quantity": ["Enter a whole number."]}}, status=status.HTTP_400_BAD_REQUEST)
		if quantity <= 0:
			item.delete()
			return cart_response(request)

		product = Product.objects.active().filter(name=item.product_title).first()
		item.quantity = min(quantity, product.stock) if product else quantity
		item.save(update_fields=["quantity"])
		return cart_response(request)

	def delete(self, request, item_id):
		self.get_item(request, item_id).delete()
		return cart_response(request)


class ProvinceListView(APIView):
	def get(self, request):
		return Response(province_list())


class CheckoutValidateView(APIView):
	"""POST a partial checkout payload plus {sections: [...]} to validate one step before moving on."""

	permission_classes = [IsAuthenticated]

	def post(self, request):
		sections = [section for section in request.data.get("sections", []) if section in CHECKOUT_SECTIONS]
		_, errors = validate_checkout(request.data, sections)
		if errors:
			return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
		return Response({"valid": True})


class CheckoutView(APIView):
	"""POST {province, billing, same_as_billing, shipping, payment} to place the order."""

	permission_classes = [IsAuthenticated]

	def post(self, request):
		checkout, errors = validate_checkout(request.data)
		if errors:
			return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
		try:
			order = place_order(request.user, get_cart(request), checkout)
		except CheckoutError as error:
			return Response({"errors": {"cart": [str(error)]}}, status=status.HTTP_409_CONFLICT)
		return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
	serializer_class = OrderSerializer
	permission_classes = [IsAuthenticated]
	pagination_class = None

	def get_queryset(self):
		return self.request.user.orders.prefetch_related("items")


class OrderDetailView(generics.RetrieveAPIView):
	serializer_class = OrderSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		return self.request.user.orders.prefetch_related("items")
