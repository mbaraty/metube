from django import forms

from videos.models import Video


class UploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'video_file', 'thumbnail_file', 'description']
