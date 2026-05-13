from django import forms
from catalog.models import Variation


INPUT_CLASSES = "w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-500"

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


class CheckoutCartForm(forms.Form):
	PROVINCE_CHOICES = (
		("ON", "Ontario"),
		("BC", "British Columbia"),
		("AB", "Alberta"),
		("QC", "Quebec"),
		("MB", "Manitoba"),
		("SK", "Saskatchewan"),
		("NS", "Nova Scotia"),
		("NB", "New Brunswick"),
		("NL", "Newfoundland and Labrador"),
		("PE", "Prince Edward Island"),
	)

	province = forms.ChoiceField(
		choices=PROVINCE_CHOICES,
		widget=forms.Select(attrs={"class": INPUT_CLASSES}),
	)


class BillingForm(forms.Form):
	full_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))
	address_line_1 = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))
	address_line_2 = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))
	city = forms.CharField(max_length=120, widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))
	postal_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))
	country = forms.CharField(max_length=80, initial="Canada", widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))


class ShippingForm(forms.Form):
	full_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))
	address_line_1 = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))
	address_line_2 = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))
	city = forms.CharField(max_length=120, widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))
	postal_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))
	country = forms.CharField(max_length=80, initial="Canada", widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))


class ShippingOptionForm(forms.Form):
	same_as_billing = forms.BooleanField(required=False, initial=True)


class PaymentForm(forms.Form):
	cardholder_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))
	card_number = forms.CharField(max_length=19, widget=forms.TextInput(attrs={"class": INPUT_CLASSES, "inputmode": "numeric"}))
	expiry_month = forms.IntegerField(min_value=1, max_value=12, widget=forms.NumberInput(attrs={"class": INPUT_CLASSES}))
	expiry_year = forms.IntegerField(min_value=2026, max_value=2100, widget=forms.NumberInput(attrs={"class": INPUT_CLASSES}))
	cvv = forms.CharField(min_length=3, max_length=4, widget=forms.PasswordInput(attrs={"class": INPUT_CLASSES, "autocomplete": "off"}))


class ConfirmationForm(forms.Form):
	confirm = forms.BooleanField(
		required=True,
		label="I confirm the order details are correct.",
	)
