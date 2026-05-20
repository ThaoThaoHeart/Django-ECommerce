from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import DeleteView, RedirectView, TemplateView, UpdateView, FormView
from django.urls import reverse_lazy
from .forms import BillingForm, CheckoutCartForm, ConfirmationForm, PaymentForm, ShippingForm, ShippingOptionForm
from .mixins import CartSessionMixin
from .models import CartItem
from .services import CheckoutSessionState


class CartDetailView(CartSessionMixin, TemplateView):
	template_name = "carts/cart_detail.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		cart_items, quantity, total = self.get_cart().snapshot()

		context.update(
			{	
				"cart_items": cart_items,
				"quantity": quantity,
				"total": total,
			}
		)
		return context


class CartRemoveView(CartSessionMixin, RedirectView):
	pattern_name = "carts:cart_detail"

	def get_redirect_url(self, *args, **kwargs):
		item_id = kwargs["item_id"]
		self.get_cart().decrement_or_remove_item(item_id)

		return super().get_redirect_url(*args, **kwargs)


class CartUpdateView(CartSessionMixin, UpdateView):
	model = CartItem
	fields = ["quantity"]
	pk_url_kwarg = "item_id"
	success_url = reverse_lazy("carts:cart_detail")

	def get_queryset(self):
		cart = self.get_cart()
		if cart is None:
			return CartItem.objects.none()
		return CartItem.objects.filter(cart=cart)

	def get(self, request, *args, **kwargs):
		return redirect("carts:cart_detail")

	def form_valid(self, form):
		raw_quantity = form.cleaned_data.get("quantity", 1)
		try:
			form.instance.quantity = max(1, int(raw_quantity))
		except (TypeError, ValueError):
			form.instance.quantity = 1
		return super().form_valid(form)

	def form_invalid(self, form):
		return redirect("carts:cart_detail")


class CartRemoveItemView(CartSessionMixin, DeleteView):
	model = CartItem
	pk_url_kwarg = "item_id"
	success_url = reverse_lazy("carts:cart_detail")

	def get_queryset(self):
		cart = self.get_cart()
		if cart is None:
			return CartItem.objects.none()
		return CartItem.objects.filter(cart=cart)

	def get(self, request, *args, **kwargs):
		return redirect("carts:cart_detail")

# Checkout flow


class CheckoutCartView(LoginRequiredMixin, CartSessionMixin, FormView):
	template_name = "carts/checkout_cart.html"
	form_class = CheckoutCartForm
	login_url = reverse_lazy("login")

	def dispatch(self, request, *args, **kwargs):
		#Gate entry: if the cart is empty, send the user back to cart details.
		cart_items, _, _ = self.get_cart().snapshot()
		if not cart_items:
			return redirect("carts:cart_detail")
		return super().dispatch(request, *args, **kwargs)

	def get_initial(self):
		initial = super().get_initial()
		checkout = CheckoutSessionState(self.request)
		if checkout.get("province"):
			initial["province"] = checkout.get("province")
		return initial

	def form_valid(self, form):
		#Persist province choice and advance to billing.
		checkout = CheckoutSessionState(self.request)
		checkout.update({"province": form.cleaned_data["province"]})
		return redirect("carts:checkout_billing")

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		cart_items, quantity, subtotal = self.get_cart().snapshot()
		checkout = CheckoutSessionState(self.request)
		province = checkout.get("province")
		tax_amount, shipping_cost, grand_total = self.get_cart().tax_shipping_total(subtotal, province)

		context.update(
			{
				"cart_items": cart_items,
				"quantity": quantity,
				"subtotal": subtotal,
				"tax_amount": tax_amount,
				"shipping_cost": shipping_cost,
				"grand_total": grand_total,
			}
		)
		return context


class CheckoutBillingView(LoginRequiredMixin, TemplateView):
	template_name = "carts/checkout_billing.html"
	login_url = reverse_lazy("login")

	def _same_as_billing_selected(self, option_form):
		if option_form.is_bound:
			return bool(option_form.data.get(option_form.add_prefix("same_as_billing")))

		initial_value = option_form.initial.get("same_as_billing")
		if initial_value is None:
			initial_value = option_form.fields["same_as_billing"].initial
		return bool(initial_value)


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		checkout = CheckoutSessionState(self.request)
		checkout_data = checkout.data()
		context.setdefault("option_form", ShippingOptionForm(initial={"same_as_billing": checkout_data.get("same_as_billing", True)}))
		context.setdefault("billing_form", BillingForm(prefix="billing", initial=checkout_data.get("billing", {})))
		context.setdefault("shipping_form", ShippingForm(prefix="shipping", initial=checkout_data.get("shipping", {})))
		context["show_shipping_form"] = not self._same_as_billing_selected(context["option_form"])
		return context

	def post(self, request, *args, **kwargs):
		option_form = ShippingOptionForm(request.POST)
		billing_form = BillingForm(request.POST, prefix="billing")
		shipping_form = ShippingForm(request.POST, prefix="shipping")

		option_valid = option_form.is_valid()
		billing_valid = billing_form.is_valid()
		same_as_billing = option_form.cleaned_data.get("same_as_billing", False) if option_valid else False
		shipping_valid = same_as_billing or shipping_form.is_valid()

		if not (option_valid and billing_valid and shipping_valid):
			context = self.get_context_data(option_form=option_form, billing_form=billing_form, shipping_form=shipping_form)
			return self.render_to_response(context)

		checkout = CheckoutSessionState(request)
		checkout.update(
			{
				"same_as_billing": same_as_billing,
				"billing": billing_form.cleaned_data,
				"shipping": billing_form.cleaned_data if same_as_billing else shipping_form.cleaned_data,
			}
		)
		return redirect("carts:checkout_payment")


class CheckoutPaymentView(LoginRequiredMixin, FormView):
	template_name = "carts/checkout_payment.html"
	form_class = PaymentForm
	login_url = reverse_lazy("login")


	def get_initial(self):
		initial = super().get_initial()
		checkout_data = CheckoutSessionState(self.request).data()
		if checkout_data.get("payment"):
			initial.update(checkout_data["payment"])
		return initial

	def form_valid(self, form):
		payment_data = dict(form.cleaned_data)
		payment_data["card_number"] = payment_data["card_number"][-4:]
		payment_data.pop("cvv", None)
		CheckoutSessionState(self.request).update({"payment": payment_data})
		return redirect("carts:checkout_confirmation")


class CheckoutConfirmationView(LoginRequiredMixin, CartSessionMixin, FormView):
	template_name = "carts/checkout_confirmation.html"
	form_class = ConfirmationForm
	login_url = reverse_lazy("login")

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		checkout_data = CheckoutSessionState(self.request).data()
		cart_items, quantity, subtotal = self.get_cart().snapshot()
		province = checkout_data.get("province")
		tax_amount, shipping_cost, grand_total = self.get_cart().tax_shipping_total(subtotal, province)

		context.update(
			{
				"cart_items": cart_items,
				"quantity": quantity,
				"subtotal": subtotal,
				"province": province,
				"billing": checkout_data.get("billing", {}),
				"shipping": checkout_data.get("shipping", {}),
				"payment": checkout_data.get("payment", {}),
				"tax_amount": tax_amount,
				"shipping_cost": shipping_cost,
				"grand_total": grand_total,
			}
		)
		return context

	def form_valid(self, form):
		self.get_cart().clear_items()
		CheckoutSessionState(self.request).clear()
		return redirect("carts:cart_detail")
