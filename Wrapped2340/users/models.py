from django.contrib.auth.models import User
from django.db import models


# SpotifyUser
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, null=True)
    refresh_token = models.CharField(max_length=255, null=True)
    data_stash = models.JSONField(default=list)

    def __str__(self):
        return self.user.username

    @classmethod
    def register(cls, user):
        profile = cls(user=user)
        profile.save()

    def add_data_stash(self, data_set):
        self.data_stash.append(data_set)
        self.save()

    def get_data_stash(self):
        return self.data_stash