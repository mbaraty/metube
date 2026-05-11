from django.contrib.auth import get_user_model
from django.db import models


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='subscriptions_made',
    )
    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='subscribers',
    )
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['subscriber', 'creator'], name='uniq_subscription')
        ]

    def __str__(self):
        return f"{self.subscriber} -> {self.creator}"
