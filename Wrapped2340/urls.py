"""
URL configuration for Wrapped2340 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='home:home'), name='home_redirect'),
    path('admin/', admin.site.urls), # admin webpage url
    path('users/', include('Wrapped2340.users.urls')), # users app url
    path('home/', include('Wrapped2340.home.urls')), # home app url
    path('slides/', include('Wrapped2340.slides.urls')),  # 'Wrapped2340.slides.urls' app url here
]
