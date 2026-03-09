from django.urls import path

from . import views

app_name = "carts"

urlpatterns = [
	path("cart/", views.cart_detail, name="cart_detail"),
	path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
	path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
	path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
	path("cart/remove-item/<int:product_id>/", views.cart_remove_item, name="cart_remove_item"),
]
