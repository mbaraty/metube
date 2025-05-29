from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from likes.models import Like


def user_has_liked(video, user):
    try:
        likes = Like.objects.get(video=video, user=user)
        return True
    except MultipleObjectsReturned:
        return True
    except ObjectDoesNotExist:
        return False
