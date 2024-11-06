from django.urls import path

from . import views

app_name = "games"

urlpatterns = [
    path("whats-the-buzz", views.WhatsTheBuzzView.as_view(), name="whats-the-buzz"),
    path("whats-the-buzz-correct", views.WhatsTheBuzzCorrectView.as_view(), name="whats-the-buzz-correct"),
    path("whats-the-buzz-incorrect", views.WhatsTheBuzzIncorrectView.as_view(), name="whats-the-buzz-incorrect"),
]
