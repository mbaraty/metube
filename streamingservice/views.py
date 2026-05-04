from django.views import generic

from videos.models import Video
from streamingservice.recommendations import get_recommendations_for_user


class IndexView(generic.ListView):
    model = Video
    context_object_name = "vid_list"
    queryset = Video.objects.filter(visibility='public').order_by('-uploaded_on')
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recommendations = get_recommendations_for_user(self.request.user, limit=10)
        context['recommended_vids'] = recommendations
        return context
