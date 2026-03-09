from django.shortcuts import render

from catalog.models import Product


def home(request):
	products = Product.objects.filter(is_active=True)
	context = {
		"products": products,
	}
	return render(request, "home.html", context)
