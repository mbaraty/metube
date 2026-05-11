from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.utils import timezone

import utils
from videos.forms import UploadForm
from videos.models import Video
from users.models import Subscription
from comments.models import Comment

@login_required
def upload_video(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)  # Handle file uploads
        if form.is_valid():
            vid = form.save(commit=False)
            vid.uploaded_by = request.user
            vid.uploaded_on = timezone.now()
            vid.save()
            utils.process_uploaded_video(vid)
            return redirect("/")
    else:
        form = UploadForm()

    return render(request, "upload.html", {"form": form})

def watch_video(request, pk):
    vid = get_object_or_404(Video, pk=pk)

    viewed_key = f"viewed_video_{vid.id}"
    if not request.session.get(viewed_key):
        vid.views += 1
        vid.save(update_fields=['views'])
        request.session[viewed_key] = True

    comments = Comment.objects.filter(video=vid).select_related('user').order_by('-date_created')
    related_videos = Video.objects.filter(visibility='public', uploaded_by=vid.uploaded_by).exclude(pk=vid.pk).order_by('-uploaded_on')[:5]

    if request.user.is_authenticated:
        is_subscribed = Subscription.objects.filter(subscriber=request.user, creator=vid.uploaded_by).exists()
        return render(request, "watch.html", {"vid": vid, "user": request.user, "user_liked": utils.user_has_liked(vid, request.user), "is_subscribed": is_subscribed, "comments": comments, "related_videos": related_videos})
    else:
        return render(request, "watch.html", {"vid": vid, "user": request.user, "comments": comments, "related_videos": related_videos})
def delete_video(request, pk):
    if request.method == "POST":
        vid = get_object_or_404(Video, pk=pk)
        if request.user.is_authenticated:
            if vid.uploaded_by == request.user:
                vid.delete()
                return redirect("/")
            return watch_video(request, pk)
        return watch_video(request, pk)
    else:
        return watch_video(request, pk)
