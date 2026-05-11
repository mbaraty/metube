from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from comments.models import Comment
from videos.models import Video


@login_required
def add_comment(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    content = (request.POST.get('content') or '').strip()
    if request.method == 'POST' and content:
        Comment.objects.create(user=request.user, video=video, content=content)
    return redirect(video.get_watch_url())
