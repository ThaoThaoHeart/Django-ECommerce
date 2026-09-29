import django.db.models.deletion
from django.db import migrations, models
from django.utils.text import slugify


def link_categories(apps, schema_editor):
	Category = apps.get_model("catalog", "Category")
	Product = apps.get_model("catalog", "Product")
	for product in Product.objects.exclude(category_name=""):
		category = Category.objects.filter(name__iexact=product.category_name).first()
		if category is None:
			category = Category.objects.create(name=product.category_name, slug=slugify(product.category_name))
		product.category = category
		product.save(update_fields=["category"])


def unlink_categories(apps, schema_editor):
	Product = apps.get_model("catalog", "Product")
	for product in Product.objects.select_related("category").exclude(category=None):
		product.category_name = product.category.name
		product.save(update_fields=["category_name"])


class Migration(migrations.Migration):

	dependencies = [
		("catalog", "0003_alter_variation_variation_category"),
	]

	operations = [
		migrations.AlterModelOptions(name="category", options={"ordering": ["name"], "verbose_name_plural": "Categories"}),
		migrations.AlterModelOptions(name="product", options={"ordering": ["name"]}),
		migrations.AlterField(
			model_name="product",
			name="image",
			field=models.ImageField(blank=True, upload_to="products/"),
		),
		migrations.RenameField(model_name="product", old_name="category", new_name="category_name"),
		migrations.AddField(
			model_name="product",
			name="category",
			field=models.ForeignKey(
				blank=True,
				null=True,
				on_delete=django.db.models.deletion.SET_NULL,
				related_name="products",
				to="catalog.category",
			),
		),
		migrations.RunPython(link_categories, unlink_categories),
		migrations.RemoveField(model_name="product", name="category_name"),
	]
