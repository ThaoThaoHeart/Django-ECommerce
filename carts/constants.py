from decimal import Decimal

# code: (name, tax rate, flat shipping cost)
PROVINCES = {
	"ON": ("Ontario", Decimal("0.13"), Decimal("0.00")),
	"BC": ("British Columbia", Decimal("0.12"), Decimal("12.00")),
	"AB": ("Alberta", Decimal("0.05"), Decimal("10.00")),
	"QC": ("Quebec", Decimal("0.14975"), Decimal("9.00")),
	"MB": ("Manitoba", Decimal("0.12"), Decimal("11.00")),
	"SK": ("Saskatchewan", Decimal("0.11"), Decimal("11.00")),
	"NS": ("Nova Scotia", Decimal("0.15"), Decimal("14.00")),
	"NB": ("New Brunswick", Decimal("0.15"), Decimal("14.00")),
	"NL": ("Newfoundland and Labrador", Decimal("0.15"), Decimal("16.00")),
	"PE": ("Prince Edward Island", Decimal("0.15"), Decimal("14.00")),
}

PROVINCE_CHOICES = [(code, name) for code, (name, _, _) in PROVINCES.items()]

CENT = Decimal("0.01")
