from django.urls import path

from . import views

app_name = "home"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("invite/<str:invite_token>", views.WrappedInviteView.as_view(), name="invite"),
    path("create-duo-wrapped", views.CreateDuoWrappedView.as_view(), name="create-duo-wrapped"),
]
