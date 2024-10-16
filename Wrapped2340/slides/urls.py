from django.urls import path

from . import views

app_name = "slides"

urlpatterns = [
    path("", views.SlidesView.as_view(), name="slides"),
]
