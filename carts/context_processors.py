from django.db.models import Sum

from .models import CartItem


def cart_item_count(request):
	if request.user.is_authenticated:
		count = (
			CartItem.objects.filter(cart__user=request.user)
			.aggregate(total=Sum("quantity"))
			.get("total")
		)
		return {"cart_count": count or 0}

	session_key = request.session.session_key
	if not session_key:
		return {"cart_count": 0}

	count = (
		CartItem.objects.filter(cart__session_key=session_key)
		.aggregate(total=Sum("quantity"))
		.get("total")
	)
	return {"cart_count": count or 0}