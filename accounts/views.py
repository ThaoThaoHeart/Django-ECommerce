from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import CustomUserCreationForm, EmailAuthenticationForm

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

	def get_success_url(self):
		return reverse_lazy("home")

class UserLogoutView(LogoutView):
	next_page = reverse_lazy("home")

class ProfileView(LoginRequiredMixin, TemplateView):
	template_name = "profile.html"
	login_url = reverse_lazy("login")
