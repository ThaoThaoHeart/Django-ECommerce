from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import CustomUserCreationForm, EmailAuthenticationForm
from carts.models import Cart

class RegisterView(FormView):
	template_name = "registration/register.html"
	form_class = CustomUserCreationForm
	success_url = reverse_lazy("login")

	def form_valid(self, form):
		form.save()
		return super().form_valid(form)
		

class UserLoginView(LoginView):
	template_name = "login.html"
	authentication_form = EmailAuthenticationForm
	redirect_authenticated_user = True

	def form_valid(self, form):
		self.transfer_anonymous_cart(form.get_user())
		return super().form_valid(form)

	def transfer_anonymous_cart(self, user):
		# If a user cart already exists, preserve it and skip anonymous transfer.
		if Cart.objects.filter(user=user).exists():
			return

		session_key = self.request.session.session_key
		if not session_key:
			return

		anonymous_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
		if not anonymous_cart:
			return

		anonymous_cart.user = user
		anonymous_cart.session_key = None
		anonymous_cart.save(update_fields=["user", "session_key"])

	def get_success_url(self):
		return reverse_lazy("home")

class UserLogoutView(LogoutView):
	next_page = reverse_lazy("home")

class ProfileView(LoginRequiredMixin, TemplateView):
	template_name = "profile.html"
	login_url = reverse_lazy("login")
