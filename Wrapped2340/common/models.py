from django.db import models
from Wrapped2340.users.models import UserProfile

class Wrapped(models.Model):
    creator1 = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='creator1')
    creator2 = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='creator2', null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=False)
    caption = models.CharField(max_length=100, blank=True)
    content = models.JSONField(default=dict)

    def __str__(self):
        noun = "Public wrapped" if self.public else "Wrapped"
        time = "Created at %s" % self.time_created
        created_by = (("By %s and %s" % (self.creator1.user.username, self.creator2.user.username))
                      if self.creator2 else
                      ("By %s" % self.creator1))
        caption_text = ("Caption: \"%s\"" % self.caption) if self.caption else "No caption"
        return "%s\n%s\n%s\n%s\n%s" % (noun, created_by, time, caption_text, self.content)