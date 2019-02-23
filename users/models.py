from django.db import models
from django.contrib.auth.models import User
from reader.models import Series, Chapter, Page


class Bookmark(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='bookmarks')

    class Meta:
        unique_together = ('series', 'user')


class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='progress')
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)


__all__ = ['User', 'Bookmark', 'Progress']

