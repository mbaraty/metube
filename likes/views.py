from django.contrib.auth.decorators import login_required
from django.core.exceptions import MultipleObjectsReturned
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from likes.models import Like
from videos.models import Video

from django.contrib.auth import user_logged_in

# Create your views here.
@login_required
def toggle(request, vid_pk):
    vid = get_object_or_404(Video, pk=vid_pk)
    user = request.user

    # Check if the user has already liked the video
    like, created = Like.objects.get_or_create(user=user, video=vid)

    if not created:
        like.delete()  # Unlike if already liked
        vid.refresh_from_db()  # Refresh num_likes from DB
        liked = False
    else:
        liked = True
    return JsonResponse({"liked": liked, "likes_count": vid.num_likes})

