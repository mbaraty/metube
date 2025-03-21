from django.contrib.auth import get_user_model
from django.db import models

from streamingservice.settings import MEDIA_ROOT, MEDIA_URL


# Create your models here.
class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    uploaded_on = models.DateTimeField()
    views = models.IntegerField(default=0)
    video_file = models.FileField(upload_to="videos/%Y/%m/%d/")
    thumbnail_file = models.FileField(upload_to="thumbnails/%Y/%m/%d/", null=True, blank=True)
    duration_sec = models.IntegerField(default=0)
    visibility = models.CharField(choices=[('public', 'Public'), ('unlisted', 'Unlisted'), ('private', 'Private')], default='public', max_length=10)

    def get_watch_url(self):
        return "/videos/watch/"+str(self.id)

    def get_stream_url(self):
        return MEDIA_URL + str(self.video_file)