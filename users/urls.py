from django.contrib.auth import views
from django.urls import path

from users import views as userviews

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('signup/', userviews.signup, name='signup'),
    path('profile/', userviews.profile, name='profile'),
    path('subscribe/<int:creator_id>/', userviews.toggle_subscription, name='toggle_subscription'),
]
