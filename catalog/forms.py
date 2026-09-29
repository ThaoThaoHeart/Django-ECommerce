from django import forms
from django.db.models import Q

from .models import Category


class ProductFilterForm(forms.Form):
	SORT_CHOICES = (
		("name", "Name: A to Z"),
		("-name", "Name: Z to A"),
		("price", "Price: low to high"),
		("-price", "Price: high to low"),
		("-created_at", "Newest"),
	)

	q = forms.CharField(required=False)
	category = forms.ModelChoiceField(queryset=Category.objects.all(), to_field_name="slug", required=False)
	min_price = forms.DecimalField(required=False, min_value=0)
	max_price = forms.DecimalField(required=False, min_value=0)
	in_stock = forms.BooleanField(required=False)
	sort = forms.ChoiceField(choices=SORT_CHOICES, required=False)

	def filter_queryset(self, queryset):
		# Invalid values (e.g. a non-numeric price) are dropped from cleaned_data and simply ignored.
		self.is_valid()
		data = getattr(self, "cleaned_data", {})

		if data.get("q"):
			queryset = queryset.filter(Q(name__icontains=data["q"]) | Q(description__icontains=data["q"]))
		if data.get("category"):
			queryset = queryset.filter(category=data["category"])
		if data.get("min_price") is not None:
			queryset = queryset.filter(price__gte=data["min_price"])
		if data.get("max_price") is not None:
			queryset = queryset.filter(price__lte=data["max_price"])
		if data.get("in_stock"):
			queryset = queryset.filter(stock__gt=0)

		return queryset.order_by(data.get("sort") or "name", "pk")
