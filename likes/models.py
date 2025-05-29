from django.db import models
from django.contrib.auth import get_user_model

from videos.models import Video


# Create your models here.
class Like(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.video.num_likes += 1
        self.video.save()
        super(Like, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.video.num_likes -= 1
        self.video.save()
        super(Like, self).delete(*args, **kwargs)
