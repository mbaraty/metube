
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views import generic

from videos.models import Video


class IndexView(generic.ListView):
    model = Video
    context_object_name = "vid_list"
    queryset = Video.objects.filter(visibility='public').order_by('-uploaded_on')
    template_name = 'index.html'