from django.urls import path
from likes import views

app_name = "likes"
urlpatterns = [
    path("toggle/<int:vid_pk>", views.toggle, name="toggle"),
]