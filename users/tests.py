from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from users.models import Subscription


class SubscriptionToggleTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='alice', password='pass12345')
        self.creator = get_user_model().objects.create_user(username='bob', password='pass12345')

    def test_requires_authentication(self):
        response = self.client.post(f'/accounts/subscribe/{self.creator.id}/')
        self.assertEqual(response.status_code, 302)

    def test_can_subscribe_and_unsubscribe(self):
        self.client.login(username='alice', password='pass12345')

        subscribe_response = self.client.post(f'/accounts/subscribe/{self.creator.id}/')
        self.assertEqual(subscribe_response.status_code, 200)
        self.assertJSONEqual(subscribe_response.content, {'subscribed': True})
        self.assertTrue(Subscription.objects.filter(subscriber=self.user, creator=self.creator).exists())

        unsubscribe_response = self.client.post(f'/accounts/subscribe/{self.creator.id}/')
        self.assertEqual(unsubscribe_response.status_code, 200)
        self.assertJSONEqual(unsubscribe_response.content, {'subscribed': False})
        self.assertFalse(Subscription.objects.filter(subscriber=self.user, creator=self.creator).exists())

    def test_cannot_subscribe_to_self(self):
        self.client.login(username='alice', password='pass12345')
        response = self.client.post(f'/accounts/subscribe/{self.user.id}/')
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'subscribed': False, 'error': 'cannot subscribe to yourself'})
