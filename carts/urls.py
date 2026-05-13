from django.urls import path

from . import views

app_name = "carts"

urlpatterns = [
	path("cart/", views.CartDetailView.as_view(), name="cart_detail"),
	path("cart/update/<int:item_id>/", views.CartUpdateView.as_view(), name="cart_update"),
	path("cart/remove/<int:item_id>/", views.CartRemoveView.as_view(), name="cart_remove"),
	path("cart/remove-item/<int:item_id>/", views.CartRemoveItemView.as_view(), name="cart_remove_item"),
	# Checkout flow
	path("checkout/", views.CheckoutCartView.as_view(), name="checkout_cart"),
	path("checkout/billing/", views.CheckoutBillingView.as_view(), name="checkout_billing"),
	path("checkout/payment/", views.CheckoutPaymentView.as_view(), name="checkout_payment"),
	path("checkout/confirmation/", views.CheckoutConfirmationView.as_view(), name="checkout_confirmation"),
]
