from django.urls.conf import path

from videos import views

app_name = "videos"
urlpatterns = [
    path('upload', views.upload_video, name="upload"),
    path('watch/<int:pk>', views.watch_video, name="watch")
]