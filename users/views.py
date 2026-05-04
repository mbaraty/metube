from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from users.models import Subscription
from django.contrib.auth import get_user_model


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def toggle_subscription(request, creator_id):
    creator = get_object_or_404(get_user_model(), pk=creator_id)
    if creator == request.user:
        return JsonResponse({"subscribed": False, "error": "cannot subscribe to yourself"}, status=400)

    sub, created = Subscription.objects.get_or_create(subscriber=request.user, creator=creator)
    if not created:
        sub.delete()
        return JsonResponse({"subscribed": False})
    return JsonResponse({"subscribed": True})
