from django.contrib.auth.models import User
from django.db import models

from videos.models import Video

## TODO idea- upvote + downvote; would require a votes model; could also stem into user karma

# Create your models here.
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.video.num_comments += 1
        self.video.save()
        super(Comment, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.video.num_comments -= 1
        self.video.save()
        super(Comment, self).delete(*args, **kwargs)