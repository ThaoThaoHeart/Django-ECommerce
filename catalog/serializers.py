from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
	product_count = serializers.IntegerField(read_only=True)

	class Meta:
		model = Category
		fields = ["id", "name", "slug", "product_count"]


class CategoryRefSerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields = ["name", "slug"]


class ProductSerializer(serializers.ModelSerializer):
	category = CategoryRefSerializer(read_only=True)
	image = serializers.ImageField(read_only=True, use_url=True)
	in_stock = serializers.BooleanField(source="is_in_stock", read_only=True)

	class Meta:
		model = Product
		fields = ["id", "name", "slug", "description", "price", "stock", "in_stock", "image", "category"]


class ProductDetailSerializer(ProductSerializer):
	variation_groups = serializers.SerializerMethodField()
	related = serializers.SerializerMethodField()

	class Meta(ProductSerializer.Meta):
		fields = [*ProductSerializer.Meta.fields, "variation_groups", "related"]

	def get_variation_groups(self, product):
		return [
			{
				"category": category,
				"label": category.replace("_", " ").title(),
				"options": [{"id": variation.pk, "value": variation.variation_value} for variation in variations],
			}
			for category, variations in product.get_variations_by_category().items()
		]

	def get_related(self, product):
		if not product.category:
			return []
		related = Product.objects.active().filter(category=product.category).exclude(pk=product.pk).select_related("category")[:4]
		return ProductSerializer(related, many=True, context=self.context).data
