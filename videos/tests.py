from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.utils import timezone

import utils
from videos.models import Video


class VideoProcessingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='uploader', password='pass12345')

    def test_process_uploaded_video_sets_completed_and_thumbnail(self):
        vid = Video.objects.create(
            title='vid',
            description='desc',
            uploaded_by=self.user,
            uploaded_on=timezone.now(),
            video_file='videos/sample.mp4',
        )

        utils.process_uploaded_video(vid)
        vid.refresh_from_db()

        self.assertEqual(vid.transcode_status, 'completed')
        self.assertIn('thumbnails/generated/sample.mp4.jpg', str(vid.thumbnail_file))

    def test_upload_view_calls_processing(self):
        client = Client()
        client.login(username='uploader', password='pass12345')
        video_blob = SimpleUploadedFile('upload.mp4', b'fake video bytes', content_type='video/mp4')

        with mock.patch('videos.views.utils.process_uploaded_video') as mocked_processor:
            response = client.post('/videos/upload', {
                'title': 'Uploaded title',
                'description': 'Uploaded description',
                'video_file': video_blob,
            })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertEqual(Video.objects.count(), 1)
        mocked_processor.assert_called_once()


class WatchVideoFeatureTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='watcher', password='pass12345')
        self.creator = get_user_model().objects.create_user(username='maker', password='pass12345')
        self.video = Video.objects.create(
            title='watch me', description='d', uploaded_by=self.creator, uploaded_on=timezone.now(), video_file='videos/watch.mp4', transcode_status='completed'
        )

    def test_watch_increments_views_once_per_session(self):
        client = Client()
        client.get(f'/videos/watch/{self.video.id}')
        self.video.refresh_from_db()
        self.assertEqual(self.video.views, 1)
        client.get(f'/videos/watch/{self.video.id}')
        self.video.refresh_from_db()
        self.assertEqual(self.video.views, 1)

    def test_add_comment_flow(self):
        client = Client()
        client.login(username='watcher', password='pass12345')
        response = client.post(f'/comments/add/{self.video.id}/', {'content': 'Nice video!'})
        self.assertEqual(response.status_code, 302)
        self.video.refresh_from_db()
        self.assertEqual(self.video.num_comments, 1)
