from django.urls import path

from .views import MeView


urlpatterns = [
    # API endpoints only
    path("me/", MeView.as_view(), name="me"),
]
