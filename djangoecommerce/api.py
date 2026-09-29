from rest_framework.authentication import SessionAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CsrfEnforcedSessionAuthentication(SessionAuthentication):
	"""DRF only checks CSRF for logged-in users; the cart and login endpoints need it for anonymous visitors too."""

	def authenticate(self, request):
		result = super().authenticate(request)
		if result is None:
			self.enforce_csrf(request)
		return result


class PageNumberPaginationWithTotals(PageNumberPagination):
	page_size_query_param = "page_size"
	max_page_size = 48

	def get_paginated_response(self, data):
		return Response(
			{
				"count": self.page.paginator.count,
				"page": self.page.number,
				"num_pages": self.page.paginator.num_pages,
				"start_index": self.page.start_index(),
				"end_index": self.page.end_index(),
				"results": data,
			}
		)


def form_errors(form):
	"""Flatten a Django form's errors into {field: [message, ...]}; non-field errors are under "__all__"."""
	return {field: list(messages) for field, messages in form.errors.items()}
