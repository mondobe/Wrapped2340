from django.contrib import admin
from .models import UserProfile  # If you have created models
from Wrapped2340.common.models import Wrapped

admin.site.register(UserProfile)
admin.site.register(Wrapped)