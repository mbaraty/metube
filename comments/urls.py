from django.urls import path

from comments import views

app_name = 'comments'
urlpatterns = [
    path('add/<int:video_id>/', views.add_comment, name='add_comment'),
]
