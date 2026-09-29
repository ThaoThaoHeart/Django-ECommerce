from django.db.models import Count, Q
from rest_framework import generics

from .forms import ProductFilterForm
from .models import Category, Product
from .serializers import CategorySerializer, ProductDetailSerializer, ProductSerializer


class CategoryListView(generics.ListAPIView):
	serializer_class = CategorySerializer
	pagination_class = None
	queryset = Category.objects.annotate(product_count=Count("products", filter=Q(products__is_active=True)))


class ProductListView(generics.ListAPIView):
	"""Supports ?q, ?category=<slug>, ?min_price, ?max_price, ?in_stock=true, ?sort, ?page and ?page_size."""

	serializer_class = ProductSerializer

	def get_queryset(self):
		products = Product.objects.active().select_related("category")
		return ProductFilterForm(self.request.query_params).filter_queryset(products)


class ProductDetailView(generics.RetrieveAPIView):
	serializer_class = ProductDetailSerializer
	lookup_field = "slug"
	queryset = Product.objects.active().select_related("category")
