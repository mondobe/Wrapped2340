from django.urls import path

from . import views

app_name = "urls"
urlpatterns = [
    path("link/", views.link, name="link"),
    path("login/", views.WrappedLoginView.as_view(), name="login"),
]