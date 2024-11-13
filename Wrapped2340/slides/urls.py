from django.urls import path
from . import views

app_name = "slides"

urlpatterns = [
    path('', views.SlidesView.as_view(), name='slides-home'),  # Default to Slide 1
    path('<int:page_id>/', views.SlidesView.as_view(), name='slide'),  # For any slide by page_id
]
