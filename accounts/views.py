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
		user = form.save()
		self.transfer_anonymous_cart(user)
		return super().form_valid(form)

	def transfer_anonymous_cart(self, user):
		session_key = self.request.session.session_key

		try:
			anonymous_cart = Cart.objects.get(session_key=session_key, user__isnull=True)
			
			user_cart, _ = Cart.objects.get_or_create(user=user)

			for item in anonymous_cart.items.all():
				item.cart = user_cart
				item.save()
			
			anonymous_cart.delete()
		except Cart.DoesNotExist:
			return
		

class UserLoginView(LoginView):
	template_name = "login.html"
	authentication_form = EmailAuthenticationForm
	redirect_authenticated_user = True

	def get_success_url(self):
		return reverse_lazy("home")

class UserLogoutView(LogoutView):
	next_page = reverse_lazy("home")

class ProfileView(LoginRequiredMixin, TemplateView):
	template_name = "profile.html"
	login_url = reverse_lazy("login")
