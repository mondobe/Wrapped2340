from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("sign-up/", views.SignUpView.as_view(), name="sign-up"),
    path("login/", views.WrappedLoginView.as_view(), name="login"),
    path("logout/", views.WrappedLogoutView.as_view(), name="logout"),
    path("account-settings/", views.AccountSettingsView.as_view(), name="account-settings"),
    path("change-password/", views.WrappedPasswordChangeView.as_view(), name="password-change"),
    path('link-spotify/', views.LinkSpotify.as_view(), name='link-spotify'),

]