from django.urls import path

from . import views

app_name = "games"

urlpatterns = [
    path("whats-the-buzz", views.WhatsTheBuzzView.as_view(), name="whats-the-buzz"),
]
