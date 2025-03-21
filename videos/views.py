from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.utils import timezone

from videos.forms import UploadForm
from videos.models import Video

@login_required
def upload_video(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)  # Handle file uploads
        if form.is_valid():
            vid = form.save(commit=False)
            vid.uploaded_by = request.user
            vid.uploaded_on = timezone.now()
            vid.save()
            return redirect("/")
    else:
        form = UploadForm()

    return render(request, "upload.html", {"form": form})

def watch_video(request, pk):
    vid = get_object_or_404(Video, pk=pk)
    return render(request, "watch.html", {"vid": vid})
