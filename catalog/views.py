from django.core.paginator import Paginator
from django.views.generic import DetailView
from django.shortcuts import redirect, render
from carts.forms import CartAddForm
from carts.mixins import CartSessionMixin
from carts.models import CartItem
from .models import Category, Product

def filter_products(selected_category, search_query):
	products = Product.objects.filter(is_active=True).prefetch_related("variation_set")

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


class ProductDetailView(CartSessionMixin, DetailView):
	model = Product
	template_name = "catalog/product_detail.html"
	context_object_name = "product"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.setdefault("form", CartAddForm(product=self.object))
		return context

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		form = CartAddForm(request.POST, product=self.object)
		if not form.is_valid():
			return self.render_to_response(self.get_context_data(form=form))

		selected_variations = []
		for field_name, value in form.cleaned_data.items():
			if field_name.startswith("variation_") and value is not None:
				category = field_name.replace("variation_", "", 1).replace("_", " ").title()
				selected_variations.append(f"{category}: {value.variation_value}")
		selected_variations_text = ", ".join(selected_variations)

		cart = self.get_or_create_cart()
		if cart is None:
			return redirect("catalog:product_detail", pk=self.object.pk)

		cart_item = CartItem.objects.filter(
			cart=cart,
			product_title=self.object.name,
			selected_variations=selected_variations_text,
		).first()
		quantity_to_add = form.cleaned_data["quantity"]
		if cart_item:
			cart_item.quantity = min(cart_item.quantity + quantity_to_add, self.object.stock)
			cart_item.save(update_fields=["quantity"])
		else:
			CartItem.objects.create(
				cart=cart,
				product_title=self.object.name,
				selected_variations=selected_variations_text,
				quantity=quantity_to_add,
			)

		return redirect("carts:cart_detail")
        