from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.services import merge_session_cart
from djangoecommerce.api import form_errors
from .forms import CustomUserCreationForm, EmailAuthenticationForm
from .serializers import UserSerializer


def user_response(request, status_code=status.HTTP_200_OK):
	user = UserSerializer(request.user).data if request.user.is_authenticated else None
	return Response({"user": user}, status=status_code)


def log_in(request, user):
	# The anonymous cart is keyed by session, so merge it before login() rotates the session key.
	merge_session_cart(request, user)
	login(request, user)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class MeView(APIView):
	"""The SPA calls this on load: it returns the current user and sets the CSRF cookie."""

	def get(self, request):
		return user_response(request)


class LoginView(APIView):
	def post(self, request):
		form = EmailAuthenticationForm(request, data={"username": request.data.get("email"), "password": request.data.get("password")})
		if not form.is_valid():
			return Response({"errors": form_errors(form)}, status=status.HTTP_400_BAD_REQUEST)
		log_in(request, form.get_user())
		return user_response(request)


class RegisterView(APIView):
	def post(self, request):
		form = CustomUserCreationForm(data=request.data)
		if not form.is_valid():
			return Response({"errors": form_errors(form)}, status=status.HTTP_400_BAD_REQUEST)
		log_in(request, form.save())
		return user_response(request, status.HTTP_201_CREATED)


class LogoutView(APIView):
	def post(self, request):
		logout(request)
		return user_response(request)
