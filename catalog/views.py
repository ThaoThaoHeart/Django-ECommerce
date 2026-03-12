from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Category, Product


def filter_products(selected_category, search_query):
	products = Product.objects.filter(is_active=True)

	if selected_category:
		category_obj = Category.objects.filter(slug=selected_category).first()
		if category_obj:
			products = products.filter(category__iexact=category_obj.name)
		else:
			products = products.none()

	if search_query:
		products = products.filter(name__icontains=search_query)

	return products.order_by("name")


def product_list(request):
	categories = Category.objects.all().order_by("name")
	selected_category = request.GET.get("category", "").strip()
	search_query = request.GET.get("search", "").strip()
	products = filter_products(selected_category, search_query)

	paginator = Paginator(products, 9)
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


@staff_member_required
def product_create(request):
	if request.method == "POST":
		form = ProductForm(request.POST, request.FILES)
		if form.is_valid():
			product = form.save()
			return redirect("catalog:product_detail", pk=product.pk)
	else:
		form = ProductForm()

	context = {
		"form": form,
		"page_title": "Create Product",
		"submit_label": "Create Product",
	}
	return render(request, "catalog/product_form.html", context)


@staff_member_required
def product_update(request, pk):
	product = get_object_or_404(Product, pk=pk)

	if request.method == "POST":
		form = ProductForm(request.POST, request.FILES, instance=product)
		if form.is_valid():
			product = form.save()
			return redirect("catalog:product_detail", pk=product.pk)
	else:
		form = ProductForm(instance=product)

	context = {
		"form": form,
		"product": product,
		"page_title": "Edit Product",
		"submit_label": "Save Changes",
	}
	return render(request, "catalog/product_form.html", context)
