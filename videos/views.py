from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.utils import timezone

import utils
from videos.forms import UploadForm
from videos.models import Video
from users.models import Subscription

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
    if request.user.is_authenticated:
        is_subscribed = Subscription.objects.filter(subscriber=request.user, creator=vid.uploaded_by).exists()
        return render(request, "watch.html", {"vid": vid, "user": request.user, "user_liked": utils.user_has_liked(vid, request.user), "is_subscribed": is_subscribed})
    else:
        return render(request, "watch.html", {"vid": vid, "user": request.user})
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
