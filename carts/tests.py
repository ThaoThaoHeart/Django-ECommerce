from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from catalog.models import Product, Variation
from .models import Cart, CartItem, Order

VALID_ADDRESS = {
	"full_name": "Ada Lovelace",
	"address_line_1": "1 Main St",
	"city": "Toronto",
	"postal_code": "m5v2t6",
}
VALID_PAYMENT = {
	"cardholder_name": "Ada Lovelace",
	"card_number": "4242 4242 4242 4242",
	"expiry_month": 12,
	"expiry_year": 2099,
	"cvv": "123",
}


class CartTestCase(APITestCase):
	@classmethod
	def setUpTestData(cls):
		cls.product = Product.objects.create(name="Snare Drum", slug="snare-drum", description="d", price=Decimal("100.00"), stock=5)
		cls.user = get_user_model().objects.create_user("ada@example.com", "s3cret-pass")

	def add_to_cart(self, quantity=1, **extra):
		return self.client.post(reverse("cart_items"), {"product": "snare-drum", "quantity": quantity, **extra}, format="json")


class CartApiTests(CartTestCase):
	def test_add_with_variation_caps_at_stock(self):
		black = Variation.objects.create(product=self.product, variation_category="color", variation_value="Black")
		self.add_to_cart(3, variations={"color": black.pk})
		response = self.add_to_cart(3, variations={"color": black.pk})
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["items"][0]["selected_variations"], "Color: Black")
		self.assertEqual(response.data["item_count"], 5)

	def test_add_validates_quantity_and_variations(self):
		Variation.objects.create(product=self.product, variation_category="color", variation_value="Black")
		response = self.add_to_cart(9)
		self.assertEqual(response.status_code, 400)
		self.assertIn("quantity", response.data["errors"])
		self.assertIn("variation_color", response.data["errors"])

	def test_update_and_remove(self):
		item_id = self.add_to_cart(2).data["items"][0]["id"]
		url = reverse("cart_item", args=[item_id])
		self.assertEqual(self.client.patch(url, {"quantity": 4}, format="json").data["item_count"], 4)
		self.assertEqual(self.client.patch(url, {"quantity": 99}, format="json").data["item_count"], 5)
		self.assertEqual(self.client.delete(url).data["items"], [])

	def test_cannot_touch_another_carts_items(self):
		other = Cart.objects.create(session_key="someone-else").items.create(product_title="Snare Drum", quantity=1)
		self.assertEqual(self.client.delete(reverse("cart_item", args=[other.pk])).status_code, 404)

	def test_province_quote(self):
		self.add_to_cart(2)
		data = self.client.get(reverse("cart"), {"province": "BC"}).data
		self.assertEqual((data["subtotal"], data["tax"], data["shipping_cost"], data["total"]), ("200.00", "24.00", "12.00", "236.00"))

	def test_unavailable_product_is_flagged(self):
		self.add_to_cart(1)
		Product.objects.update(is_active=False)
		data = self.client.get(reverse("cart")).data
		self.assertTrue(data["has_errors"])
		self.assertEqual(data["items"][0]["error"], "This product is no longer available.")

	def test_anonymous_writes_require_csrf(self):
		client = APIClient(enforce_csrf_checks=True)
		response = client.post(reverse("cart_items"), {"product": "snare-drum", "quantity": 1}, format="json")
		self.assertEqual(response.status_code, 403)

		client.get(reverse("me"))
		token = client.cookies["csrftoken"].value
		response = client.post(reverse("cart_items"), {"product": "snare-drum", "quantity": 1}, format="json", HTTP_X_CSRFTOKEN=token)
		self.assertEqual(response.status_code, 201)


class AuthApiTests(CartTestCase):
	def test_login_merges_session_cart_into_user_cart(self):
		Cart.objects.create(user=self.user).items.create(product_title="Snare Drum", quantity=1)
		self.add_to_cart(2)

		response = self.client.post(reverse("login"), {"email": "ada@example.com", "password": "s3cret-pass"}, format="json")
		self.assertEqual(response.data["user"]["email"], "ada@example.com")
		self.assertEqual(Cart.objects.count(), 1)
		self.assertEqual(self.client.get(reverse("cart")).data["item_count"], 3)

	def test_bad_login(self):
		response = self.client.post(reverse("login"), {"email": "ada@example.com", "password": "nope"}, format="json")
		self.assertEqual(response.status_code, 400)
		self.assertIn("__all__", response.data["errors"])

	def test_register_logs_in_and_keeps_cart(self):
		self.add_to_cart(1)
		response = self.client.post(
			reverse("register"),
			{"email": "new@Example.COM", "password1": "a-long-passphrase", "password2": "a-long-passphrase"},
			format="json",
		)
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["user"]["email"], "new@example.com")
		self.assertEqual(self.client.get(reverse("cart")).data["item_count"], 1)

	def test_logout(self):
		self.client.force_login(self.user)
		self.assertIsNone(self.client.post(reverse("logout")).data["user"])
		self.assertIsNone(self.client.get(reverse("me")).data["user"])


class CheckoutApiTests(CartTestCase):
	def setUp(self):
		self.client.force_login(self.user)

	def payload(self, **overrides):
		return {
			"province": "BC",
			"billing": VALID_ADDRESS,
			"same_as_billing": False,
			"shipping": {**VALID_ADDRESS, "city": "Vancouver", "postal_code": "V6B 1A1"},
			"payment": VALID_PAYMENT,
			**overrides,
		}

	def checkout(self, **overrides):
		return self.client.post(reverse("checkout"), self.payload(**overrides), format="json")

	def test_requires_login(self):
		self.client.logout()
		self.assertEqual(self.checkout().status_code, 403)
		self.assertEqual(self.client.get(reverse("order_list")).status_code, 403)

	def test_validate_single_step(self):
		response = self.client.post(
			reverse("checkout_validate"),
			{"sections": ["payment"], "payment": {**VALID_PAYMENT, "card_number": "4242 4242 4242 4241", "expiry_year": 2001}},
			format="json",
		)
		self.assertEqual(response.status_code, 400)
		self.assertEqual(set(response.data["errors"]), {"payment"})
		self.assertIn("card_number", response.data["errors"]["payment"])
		self.assertEqual(response.data["errors"]["payment"]["__all__"], ["This card has expired."])

	def test_same_as_billing_skips_shipping_validation(self):
		response = self.client.post(
			reverse("checkout_validate"), {"sections": ["billing", "shipping"], "billing": VALID_ADDRESS, "same_as_billing": True}, format="json"
		)
		self.assertEqual(response.status_code, 200)

	def test_empty_cart_is_rejected(self):
		response = self.checkout()
		self.assertEqual(response.status_code, 409)
		self.assertFalse(Order.objects.exists())

	def test_full_checkout_creates_order_and_decrements_stock(self):
		self.add_to_cart(2)
		response = self.checkout()
		self.assertEqual(response.status_code, 201)

		order = Order.objects.get()
		self.assertEqual(response.data["number"], order.number)
		self.assertEqual((order.subtotal, order.tax, order.shipping_cost, order.total), (Decimal("200.00"), Decimal("24.00"), Decimal("12.00"), Decimal("236.00")))
		self.assertEqual(order.shipping_address["city"], "Vancouver")
		self.assertEqual(order.billing_address["postal_code"], "M5V 2T6")
		self.assertEqual(order.card_last4, "4242")
		self.assertNotIn("4242 4242", str(order.billing_address) + str(order.shipping_address))

		self.product.refresh_from_db()
		self.assertEqual(self.product.stock, 3)
		self.assertFalse(CartItem.objects.exists())
		self.assertEqual([o["id"] for o in self.client.get(reverse("order_list")).data], [order.pk])

	def test_stock_sold_out_before_order(self):
		self.add_to_cart(2)
		Product.objects.update(stock=1)
		self.assertEqual(self.checkout().status_code, 409)
		self.assertFalse(Order.objects.exists())

	def test_orders_are_private(self):
		other = get_user_model().objects.create_user("bob@example.com", "pw")
		order = Order.objects.create(
			user=other, province="ON", billing_address={}, shipping_address={}, cardholder_name="Bob",
			card_last4="0000", subtotal=0, tax=0, shipping_cost=0, total=0,
		)
		self.assertEqual(self.client.get(reverse("order_detail", args=[order.pk])).status_code, 404)
