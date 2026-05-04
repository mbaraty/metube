from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from django.db.models import F, FloatField, Q, Value
from django.db.models.expressions import ExpressionWrapper
from django.db.models.functions import Coalesce
from django.utils import timezone

from users.models import Subscription
from videos.models import Video


@dataclass(frozen=True)
class RecommendationItem:
    video: Video
    score: float
    reason: str


def _base_queryset(user):
    qs = Video.objects.filter(visibility='public', transcode_status='completed')
    if user.is_authenticated:
        qs = qs.exclude(uploaded_by=user)
    return qs


def get_recommendations_for_user(user, *, limit: int = 10) -> list[RecommendationItem]:
    now = timezone.now()
    week_ago = now - timedelta(days=7)

    base = _base_queryset(user).annotate(
        recency_bonus=ExpressionWrapper(
            Value(1.0) / (Value(1.0) + Coalesce(F('views'), Value(0.0)) * Value(0.0) + Value(0.05)),
            output_field=FloatField(),
        ),
        popularity_score=ExpressionWrapper(
            Coalesce(F('num_likes'), Value(0.0)) * Value(3.0)
            + Coalesce(F('num_comments'), Value(0.0)) * Value(2.0)
            + Coalesce(F('views'), Value(0.0)) * Value(0.2),
            output_field=FloatField(),
        ),
        freshness_score=ExpressionWrapper(
            Value(20.0),
            output_field=FloatField(),
        ),
    )

    subscribed_creator_ids = []
    if user.is_authenticated:
        subscribed_creator_ids = list(
            Subscription.objects.filter(subscriber=user).values_list('creator_id', flat=True)
        )

    if subscribed_creator_ids:
        personalized = base.filter(uploaded_by_id__in=subscribed_creator_ids).annotate(
            total_score=ExpressionWrapper(F('popularity_score') + Value(50.0), output_field=FloatField())
        ).order_by('-total_score', '-uploaded_on')[:limit]

        fallback = base.exclude(id__in=personalized.values('id')).annotate(
            total_score=ExpressionWrapper(
                F('popularity_score') + Value(10.0), output_field=FloatField()
            )
        ).order_by('-total_score', '-uploaded_on')[: max(limit - personalized.count(), 0)]

        ordered = list(personalized) + list(fallback)
        return [RecommendationItem(video=v, score=getattr(v, 'total_score', 0.0), reason='From channels you subscribed to' if v.uploaded_by_id in subscribed_creator_ids else 'Popular right now') for v in ordered[:limit]]

    trending = base.filter(uploaded_on__gte=week_ago).annotate(
        total_score=ExpressionWrapper(F('popularity_score') + Value(25.0), output_field=FloatField())
    ).order_by('-total_score', '-uploaded_on')[:limit]

    if trending:
        return [RecommendationItem(video=v, score=getattr(v, 'total_score', 0.0), reason='Trending this week') for v in trending]

    recent = base.annotate(
        total_score=ExpressionWrapper(F('popularity_score') + Value(5.0), output_field=FloatField())
    ).order_by('-uploaded_on')[:limit]
    return [RecommendationItem(video=v, score=getattr(v, 'total_score', 0.0), reason='Recently uploaded') for v in recent]
