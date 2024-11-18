import secrets

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models



# SpotifyUser
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, null=True)
    refresh_token = models.CharField(max_length=255, null=True)
    invite_token = models.CharField(max_length=16)

    def __str__(self):
        return self.user.username

    @classmethod
    def register(cls, user):
        profile = cls(user=user)
        profile.rotate_invite_token()
        profile.save()


    def rotate_invite_token(self):
        self.invite_token = self.create_invite_token()

    def create_invite_token(self):
        long_username = "%suser" % self.user.username
        return "%s%s" % (long_username[0:4], secrets.token_urlsafe(9))


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}: {self.message[:20]}"
