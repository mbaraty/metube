from pathlib import Path

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from likes.models import Like


def user_has_liked(video, user):
    try:
        Like.objects.get(video=video, user=user)
        return True
    except MultipleObjectsReturned:
        return True
    except ObjectDoesNotExist:
        return False


def process_uploaded_video(video):
    """Best-effort local processing to emulate transcoding + thumbnail generation."""
    try:
        video.transcode_status = 'processing'
        video.save(update_fields=['transcode_status'])

        # Placeholder for real transcoding pipeline.
        video.transcode_status = 'completed'

        if not video.thumbnail_file:
            thumb_name = Path(video.video_file.name).name + '.jpg'
            video.thumbnail_file = f"thumbnails/generated/{thumb_name}"

        video.save(update_fields=['transcode_status', 'thumbnail_file'])
    except Exception:
        video.transcode_status = 'failed'
        video.save(update_fields=['transcode_status'])
