from django.db import models
from django.contrib.auth.models import User
from reader.models import Series


class Bookmark(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")

    class Meta:
        unique_together = ('series', 'user')
