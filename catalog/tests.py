from decimal import Decimal

from django.urls import reverse
from django.utils.text import slugify
from rest_framework.test import APITestCase

from .models import Category, Product, Variation


def make_product(name, category=None, price="10.00", stock=5, **kwargs):
	return Product.objects.create(
		name=name, slug=slugify(name), description=f"{name} description", price=Decimal(price),
		stock=stock, category=category, **kwargs,
	)


class ProductListTests(APITestCase):
	@classmethod
	def setUpTestData(cls):
		cls.guitars = Category.objects.create(name="Guitars")
		cls.drums = Category.objects.create(name="Drums")
		make_product("Acoustic Guitar", cls.guitars, price="300.00")
		make_product("Bass Guitar", cls.guitars, price="500.00", stock=0)
		make_product("Snare Drum", cls.drums, price="150.00")
		make_product("Hidden Drum", cls.drums, is_active=False)

	def names(self, **params):
		response = self.client.get(reverse("product_list"), params)
		self.assertEqual(response.status_code, 200)
		return [product["name"] for product in response.data["results"]]

	def test_lists_active_products_only(self):
		self.assertEqual(self.names(), ["Acoustic Guitar", "Bass Guitar", "Snare Drum"])

	def test_category_filter(self):
		self.assertEqual(self.names(category="drums"), ["Snare Drum"])

	def test_search_matches_name_and_description(self):
		self.assertEqual(self.names(q="guitar"), ["Acoustic Guitar", "Bass Guitar"])
		self.assertEqual(self.names(q="snare drum description"), ["Snare Drum"])

	def test_price_range_and_stock_filters(self):
		self.assertEqual(self.names(min_price="200", max_price="400"), ["Acoustic Guitar"])
		self.assertEqual(self.names(category="guitars", in_stock="true"), ["Acoustic Guitar"])

	def test_sort(self):
		self.assertEqual(self.names(sort="-price"), ["Bass Guitar", "Acoustic Guitar", "Snare Drum"])

	def test_invalid_params_are_ignored(self):
		self.assertEqual(len(self.names(min_price="abc", category="nope", sort="bogus")), 3)

	def test_pagination(self):
		for index in range(12):
			make_product(f"Guitar Pick {index:02d}", self.guitars)
		response = self.client.get(reverse("product_list"), {"q": "pick", "page": 2})
		self.assertEqual((response.data["count"], response.data["page"], response.data["num_pages"]), (12, 2, 2))
		self.assertEqual(len(response.data["results"]), 3)

	def test_categories_include_active_counts(self):
		counts = {category["slug"]: category["product_count"] for category in self.client.get(reverse("category_list")).data}
		self.assertEqual(counts, {"drums": 1, "guitars": 2})


class ProductDetailTests(APITestCase):
	def test_detail_groups_variations_and_lists_related(self):
		guitars = Category.objects.create(name="Guitars")
		product = make_product("Acoustic Guitar", guitars)
		make_product("Bass Guitar", guitars)
		Variation.objects.create(product=product, variation_category="key_count", variation_value="88 Keys")

		data = self.client.get(reverse("product_detail", args=[product.slug])).data
		self.assertEqual(data["variation_groups"][0]["label"], "Key Count")
		self.assertEqual([related["name"] for related in data["related"]], ["Bass Guitar"])

	def test_inactive_product_is_404(self):
		make_product("Retired", is_active=False)
		self.assertEqual(self.client.get(reverse("product_detail", args=["retired"])).status_code, 404)
