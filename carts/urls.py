from django.urls import path

from . import views

app_name = "carts"

urlpatterns = [
	path("cart/", views.CartDetailView.as_view(), name="cart_detail"),
	path("cart/add/<int:product_id>/", views.CartAddView.as_view(), name="cart_add"),
	path("cart/update/<int:item_id>/", views.CartUpdateView.as_view(), name="cart_update"),
	path("cart/remove/<int:item_id>/", views.CartRemoveView.as_view(), name="cart_remove"),
	path("cart/remove-item/<int:item_id>/", views.CartRemoveItemView.as_view(), name="cart_remove_item"),
]
