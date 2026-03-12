from django.forms import ModelForm
from .models import Product


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "slug",
            "description",
            "price",
            "stock",
            "image",
            "category",
            "is_active",
        ]
                