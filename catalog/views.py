from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator

from .models import Category, Product


def product_list(request):
	products = Product.objects.filter(is_active=True)
	categories = Category.objects.all().order_by("name")
	selected_category = request.GET.get("category", "").strip()
	search_query = request.GET.get("search", "").strip()

	if selected_category:
		category_obj = Category.objects.filter(slug=selected_category).first()
		if category_obj:
			products = products.filter(category__iexact=category_obj.name)
		else:
			products = products.none()

	if search_query:
		products = products.filter(name__icontains=search_query)

	paginator = Paginator(products.order_by("name"), 9)
	page_number = request.GET.get("page")
	page_obj = paginator.get_page(page_number)

	context = {
		"products": page_obj.object_list,
		"page_obj": page_obj,
		"categories": categories,
		"selected_category": selected_category,
		"search_query": search_query,
	}
	return render(request, "catalog/product_list.html", context)


def product_detail(request, pk):
	product = get_object_or_404(Product, pk=pk, is_active=True)
	context = {
		"product": product,
	}
	return render(request, "catalog/product_detail.html", context)
