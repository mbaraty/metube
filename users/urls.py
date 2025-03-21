from django.urls.conf import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'
urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("profile/", views.ProfileView.as_view(), name="profile")
]
