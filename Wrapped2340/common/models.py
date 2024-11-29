from django.db import models
from Wrapped2340.users.models import UserProfile

class Wrapped(models.Model):
    version = models.CharField(max_length=20)
    creator1 = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='creator1')
    creator2 = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='creator2', null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=False)
    caption = models.CharField(max_length=100, blank=True)
    content = models.JSONField(default=dict)

    def default_content(self):
        if self.creator2:
            return self.content['duo1']
        else:
            return self.content

    def __str__(self):
        noun = "Public wrapped" if self.public else "Wrapped"
        time = "Created at %s" % self.time_created
        created_by = (("By %s and %s" % (self.creator1.user.username, self.creator2.user.username))
                      if self.creator2 else
                      ("By %s" % self.creator1))
        caption_text = ("Caption: \"%s\"" % self.caption) if self.caption else "No caption"
        return "%s\n%s\n%s\n%s" % (noun, created_by, time, caption_text)


class CommonFeedback(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Feedback: {self.message[:20]}"

class PreviewUrl(models.Model):
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255, null=True)
    url = models.TextField()

    def __str__(self):
        return f"Name: {self.name}"