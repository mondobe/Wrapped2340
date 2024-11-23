from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "home"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name='home:discover'), name="home-redirect"),
    path("my-wraps", views.HomeView.as_view(), name="home"),
    path("discover", views.DiscoverView.as_view(), name="discover"),
    path("invite/<str:invite_token>", views.WrappedInviteView.as_view(), name="invite"),
    path("create-duo-wrapped", views.CreateDuoWrappedView.as_view(), name="create-duo-wrapped"),
]
