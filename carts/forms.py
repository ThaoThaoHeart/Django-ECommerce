import re

from django import forms
from django.core.validators import MaxValueValidator
from django.utils import timezone

from catalog.models import Variation
from djangoecommerce.api import form_errors
from .constants import PROVINCE_CHOICES


class CartAddForm(forms.Form):
	quantity = forms.IntegerField(min_value=1)

	def __init__(self, *args, product, **kwargs):
		self.product = product
		super().__init__(*args, **kwargs)
		self.fields["quantity"].validators.append(MaxValueValidator(product.stock, f"Only {product.stock} available."))

		for category, variations in product.get_variations_by_category().items():
			self.fields[f"variation_{category}"] = forms.ModelChoiceField(
				queryset=Variation.objects.filter(pk__in=[variation.pk for variation in variations]),
				label=category.replace("_", " ").title(),
			)

	def clean(self):
		if not self.product.is_in_stock():
			raise forms.ValidationError("This product is out of stock.")
		return super().clean()

	def selected_variations(self):
		return ", ".join(
			f"{self.fields[name].label}: {value.variation_value}"
			for name, value in self.cleaned_data.items()
			if name.startswith("variation_")
		)


class ProvinceForm(forms.Form):
	province = forms.ChoiceField(choices=PROVINCE_CHOICES)


class AddressForm(forms.Form):
	full_name = forms.CharField(max_length=200)
	address_line_1 = forms.CharField(max_length=255)
	address_line_2 = forms.CharField(max_length=255, required=False)
	city = forms.CharField(max_length=120)
	postal_code = forms.CharField(max_length=7)

	def clean_postal_code(self):
		code = self.cleaned_data["postal_code"].upper().replace(" ", "")
		if not re.fullmatch(r"[A-Z]\d[A-Z]\d[A-Z]\d", code):
			raise forms.ValidationError("Enter a valid Canadian postal code, e.g. A1A 1A1.")
		return f"{code[:3]} {code[3:]}"


class PaymentForm(forms.Form):
	cardholder_name = forms.CharField(max_length=200)
	card_number = forms.CharField(max_length=23)
	expiry_month = forms.IntegerField(min_value=1, max_value=12)
	expiry_year = forms.IntegerField(min_value=2000, max_value=2100)
	cvv = forms.CharField(min_length=3, max_length=4)

	def clean_card_number(self):
		digits = re.sub(r"[\s-]", "", self.cleaned_data["card_number"])
		if not digits.isdigit() or not 12 <= len(digits) <= 19 or not luhn_valid(digits):
			raise forms.ValidationError("Enter a valid card number.")
		return digits

	def clean_cvv(self):
		cvv = self.cleaned_data["cvv"]
		if not cvv.isdigit():
			raise forms.ValidationError("CVV must be digits only.")
		return cvv

	def clean(self):
		cleaned = super().clean()
		month, year = cleaned.get("expiry_month"), cleaned.get("expiry_year")
		today = timezone.localdate()
		if month and year and (year, month) < (today.year, today.month):
			raise forms.ValidationError("This card has expired.")
		return cleaned


def luhn_valid(digits):
	total = 0
	for index, digit in enumerate(reversed(digits)):
		value = int(digit)
		if index % 2:
			value = value * 2 - 9 if value > 4 else value * 2
		total += value
	return total % 10 == 0


# Checkout payload section -> form that validates it. "province" is a bare code, the rest are objects.
CHECKOUT_SECTIONS = {
	"province": ProvinceForm,
	"billing": AddressForm,
	"shipping": AddressForm,
	"payment": PaymentForm,
}


def validate_checkout(data, sections=CHECKOUT_SECTIONS):
	"""Validate the requested sections of a checkout payload. Returns (cleaned, errors) keyed by section."""
	cleaned, errors = {}, {}
	for section in sections:
		if section == "shipping" and data.get("same_as_billing"):
			continue
		section_data = {"province": data.get("province")} if section == "province" else data.get(section) or {}
		form = CHECKOUT_SECTIONS[section](section_data)
		if not form.is_valid():
			errors[section] = form_errors(form)
		elif section == "province":
			cleaned[section] = form.cleaned_data["province"]
		else:
			cleaned[section] = form.cleaned_data

	if data.get("same_as_billing") and "billing" in cleaned and "shipping" in sections:
		cleaned["shipping"] = cleaned["billing"]
	return cleaned, errors
