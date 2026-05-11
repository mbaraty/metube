from django.db.models import Q
from django.views import generic

from users.models import Subscription
from videos.models import Video
from streamingservice.recommendations import get_recommendations_for_user


class IndexView(generic.ListView):
    model = Video
    context_object_name = "vid_list"
    queryset = Video.objects.filter(visibility='public').order_by('-uploaded_on')
    template_name = 'index.html'

    def get_queryset(self):
        queryset = Video.objects.filter(visibility='public')
        query = (self.request.GET.get('q') or '').strip()
        sort = self.request.GET.get('sort', 'latest')

        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))

        if sort == 'popular':
            queryset = queryset.order_by('-num_likes', '-views', '-uploaded_on')
        else:
            queryset = queryset.order_by('-uploaded_on')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recommendations = get_recommendations_for_user(self.request.user, limit=10)
        context['recommended_vids'] = recommendations
        context['query'] = (self.request.GET.get('q') or '').strip()
        context['sort'] = self.request.GET.get('sort', 'latest')

        if self.request.user.is_authenticated:
            subscribed_ids = Subscription.objects.filter(subscriber=self.request.user).values_list('creator_id', flat=True)
            context['subscription_vids'] = Video.objects.filter(visibility='public', uploaded_by_id__in=subscribed_ids).order_by('-uploaded_on')[:10]
        else:
            context['subscription_vids'] = []
        return context
