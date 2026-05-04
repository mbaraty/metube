from django.views import generic

from users.models import Subscription
from videos.models import Video


class IndexView(generic.ListView):
    model = Video
    context_object_name = "vid_list"
    queryset = Video.objects.filter(visibility='public').order_by('-uploaded_on')
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recommendations = Video.objects.filter(visibility='public').order_by('-num_likes', '-views', '-uploaded_on')[:10]

        if self.request.user.is_authenticated:
            subscribed_ids = Subscription.objects.filter(
                subscriber=self.request.user
            ).values_list('creator_id', flat=True)
            personalized = Video.objects.filter(
                visibility='public', uploaded_by_id__in=subscribed_ids
            ).order_by('-uploaded_on')[:10]
            if personalized:
                recommendations = personalized

        context['recommended_vids'] = recommendations
        return context
