from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from streamingservice.recommendations import get_recommendations_for_user
from users.models import Subscription
from videos.models import Video


class RecommendationPipelineTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='viewer', password='pass12345')
        self.creator_a = get_user_model().objects.create_user(username='creator_a', password='pass12345')
        self.creator_b = get_user_model().objects.create_user(username='creator_b', password='pass12345')

    def _make_video(self, creator, title, likes=0, comments=0, views=0, days_ago=0, status='completed', visibility='public'):
        return Video.objects.create(
            title=title,
            description='d',
            uploaded_by=creator,
            uploaded_on=timezone.now() - timezone.timedelta(days=days_ago),
            views=views,
            num_likes=likes,
            num_comments=comments,
            transcode_status=status,
            visibility=visibility,
            video_file=f'videos/{title}.mp4',
        )

    def test_subscription_content_prioritized(self):
        Subscription.objects.create(subscriber=self.user, creator=self.creator_a)
        subscribed_video = self._make_video(self.creator_a, 'subbed', likes=1)
        other_video = self._make_video(self.creator_b, 'other', likes=999)

        recs = get_recommendations_for_user(self.user, limit=5)

        self.assertGreaterEqual(len(recs), 1)
        self.assertEqual(recs[0].video.id, subscribed_video.id)
        self.assertEqual(recs[0].reason, 'From channels you subscribed to')
        self.assertIn(other_video.id, [rec.video.id for rec in recs])

    def test_trending_fallback_without_subscriptions(self):
        self._make_video(self.creator_b, 'trend', likes=10, comments=4, views=50, days_ago=1)
        recs = get_recommendations_for_user(self.user, limit=3)
        self.assertGreaterEqual(len(recs), 1)
        self.assertEqual(recs[0].reason, 'Trending this week')

    def test_filters_out_private_or_unprocessed(self):
        self._make_video(self.creator_b, 'private_video', visibility='private')
        self._make_video(self.creator_b, 'pending_video', status='pending')
        good = self._make_video(self.creator_b, 'good_video', status='completed', visibility='public')

        recs = get_recommendations_for_user(self.user, limit=10)
        rec_ids = [rec.video.id for rec in recs]

        self.assertIn(good.id, rec_ids)
        titles = [rec.video.title for rec in recs]
        self.assertNotIn('private_video', titles)
        self.assertNotIn('pending_video', titles)


class IndexFeatureTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='indexer', password='pass12345')
        self.creator = get_user_model().objects.create_user(username='creator_idx', password='pass12345')

    def test_search_and_sort(self):
        Video.objects.create(title='Alpha', description='hello', uploaded_by=self.creator, uploaded_on=timezone.now(), video_file='videos/a.mp4', transcode_status='completed', num_likes=1)
        Video.objects.create(title='Beta', description='hello', uploaded_by=self.creator, uploaded_on=timezone.now(), video_file='videos/b.mp4', transcode_status='completed', num_likes=99)
        self.client.login(username='indexer', password='pass12345')
        response = self.client.get('/?q=Beta&sort=popular')
        self.assertContains(response, 'Beta')
        listed_titles = [v.title for v in response.context['vid_list']]
        self.assertEqual(listed_titles, ['Beta'])

    def test_subscription_feed_section(self):
        Subscription.objects.create(subscriber=self.user, creator=self.creator)
        Video.objects.create(title='Sub feed vid', description='d', uploaded_by=self.creator, uploaded_on=timezone.now(), video_file='videos/s.mp4', transcode_status='completed')
        self.client.login(username='indexer', password='pass12345')
        response = self.client.get('/')
        self.assertContains(response, 'From your subscriptions')
        self.assertContains(response, 'Sub feed vid')
