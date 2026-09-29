from django.urls import path
from .views import LoginView, LogoutView, MeView, RegisterView

urlpatterns = [
    path("auth/me/", MeView.as_view(), name="me"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/register/", RegisterView.as_view(), name="register"),
]
