from django.db import models


# SpotifyUser
class UserProfile(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    spotify_id = models.CharField(max_length=50, unique=True)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    token_expires = models.DateTimeField()

    def __str__(self):
        return self.username
