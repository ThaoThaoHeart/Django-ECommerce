from django.core.paginator import Paginator
from django.views.generic import FormView
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from carts.forms import CartAddForm
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


class ProductDetailView(FormView):
	template_name = "catalog/product_detail.html"
	form_class = CartAddForm
	success_url = reverse_lazy("carts:cart_detail")

	def get_product(self):
		return get_object_or_404(Product, pk=self.kwargs["pk"], is_active=True)

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs["product"] = self.get_product()
		return kwargs

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["product"] = self.get_product()
		return context

