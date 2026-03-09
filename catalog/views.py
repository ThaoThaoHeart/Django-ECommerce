from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def product_list(request):
	products = Product.objects.filter(is_active=True)
	context = {
		"products": products,
	}
	return render(request, "catalog/product_list.html", context)


def product_detail(request, pk):
	product = get_object_or_404(Product, pk=pk, is_active=True)
	context = {
		"product": product,
	}
	return render(request, "catalog/product_detail.html", context)
