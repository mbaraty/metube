from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from django.contrib.auth import get_user_model
from django.urls.base import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("users:login")
    template_name = "registration/signup.html"



class ProfileView(UpdateView):
    model = get_user_model()
    success_url = reverse_lazy("index")
    template_name = "registration/profile.html"
    fields = ["username", "first_name", "last_name", "email"]  # Fixed field names

    def get_object(self, queryset=None):
        return self.request.user  # Ensure the logged-in user is the object being updated