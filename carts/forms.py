from django import forms
from catalog.models import Variation

class CartAddForm(forms.Form):
	quantity = forms.IntegerField(min_value=1, initial=1)

	def __init__(self, *args, product=None, **kwargs):
		self.product = product
		super().__init__(*args, **kwargs)

		if not self.product:
			return

		variation_groups = self.product.get_variations_by_category()
		for category, variations in variation_groups.items():
			variation_ids = [variation.pk for variation in variations]
			if not variation_ids:
				continue

			field_name = f"variation_{category}"
			self.fields[field_name] = forms.ModelChoiceField(
				queryset=Variation.objects.filter(pk__in=variation_ids).order_by("variation_value"),
				empty_label=None,
				required=True,
				label=category.replace("_", " ").title(),
				widget=forms.Select(
					attrs={
						"class": "w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-500",
					}
				),
			)

	def clean_quantity(self):
		quantity = self.cleaned_data["quantity"]
		if self.product:
			quantity = min(quantity, self.product.stock)
		return quantity
