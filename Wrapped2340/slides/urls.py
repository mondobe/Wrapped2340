from django.urls import path
from . import views

app_name = "slides"

urlpatterns = [
    path('<int:page_id>/', views.SlidesView.as_view(), name='slide'),
]
