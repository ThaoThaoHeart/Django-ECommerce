from django import forms

from catalog.models import Variation


class VariationChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.variation_value


class CartAddForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "w-20 border rounded px-3 py-2", "min": 1}),
    )

    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product

        if not self.product:
            return

        variation_qs = (
            Variation.objects.filter(product=self.product, is_active=True)
            .order_by("variation_category", "variation_value")
        )
        categories = variation_qs.values_list("variation_category", flat=True).distinct()

        for category in categories:
            field_name = f"variation_{category}"
            category_qs = variation_qs.filter(variation_category=category)
            label = category.replace("_", " ").title()
            self.fields[field_name] = VariationChoiceField(
                queryset=category_qs,
                required=False,
                label=label,
                empty_label=f"Select {label}",
                widget=forms.Select(attrs={"class": "w-full border rounded px-3 py-2"}),
            )

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if self.product:
            return min(quantity, self.product.stock)
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        selected_variations = []

        for field_name, value in cleaned_data.items():
            if field_name.startswith("variation_") and value:
                selected_variations.append(value)

        cleaned_data["selected_variations"] = selected_variations
        return cleaned_data
