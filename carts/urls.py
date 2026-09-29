from django.urls import path

from . import views

urlpatterns = [
	path("cart/", views.CartView.as_view(), name="cart"),
	path("cart/items/", views.CartItemListView.as_view(), name="cart_items"),
	path("cart/items/<int:item_id>/", views.CartItemDetailView.as_view(), name="cart_item"),
	path("provinces/", views.ProvinceListView.as_view(), name="provinces"),
	path("checkout/validate/", views.CheckoutValidateView.as_view(), name="checkout_validate"),
	path("checkout/", views.CheckoutView.as_view(), name="checkout"),
	path("orders/", views.OrderListView.as_view(), name="order_list"),
	path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
]
