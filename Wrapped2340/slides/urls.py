from django.urls import path
from . import views

app_name = "slides"

urlpatterns = [
    path('<int:wrapped_id>/<int:page_id>/', views.SlidesView.as_view(), name='slide'),  # For any slide by page_id
]
