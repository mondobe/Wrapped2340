from django.contrib.auth.models import User
from django.db import models


# SpotifyUser
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=50, unique=True, null=True)
    access_token = models.CharField(max_length=255, null=True)
    refresh_token = models.CharField(max_length=255, null=True)
    token_expires = models.DateTimeField(null=True)

    def __str__(self):
        return self.user.username

    @classmethod
    def register(cls, user):
        profile = cls(user=user)
        profile.save()