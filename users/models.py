from django.contrib.auth.models import User
from django.db import models

from MangAdventure.utils import storage, uploaders, validators
from reader.models import Chapter, Series


class Bookmark(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bookmarks'
    )

    class Meta:
        unique_together = ('series', 'user')


# TODO: add user preferences

class UserProfile(models.Model):
    _validator = validators.FileSizeValidator(max_mb=2)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )
    bio = models.TextField(
        blank=True, verbose_name='biography',
        help_text="The user's biography."
    )
    avatar = models.ImageField(
        storage=storage.OverwriteStorage(),
        upload_to=uploaders.avatar_uploader,
        help_text="The user's avatar image. Must be "
                  "up to %d MBs." % _validator.max_mb,
        validators=(_validator,), blank=True
    )
    bookmarks = models.ManyToManyField(
        Bookmark, related_name='profile', blank=True,
        help_text="The user's bookmarked series."
    )
    # TODO: add links and let users choose whether to display their e-mail

    def __str__(self):
        return str(self.user)


# Might be utilised for progress tracking in the future
class Progress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='progress'
    )
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    last_update = models.DateTimeField(auto_now=True)

    def save(self, **kwargs):
        # Delete old progress before saving
        Progress.objects.filter(
            user_id=self.user.id, chapter__series_id=self.chapter.series.id
        ).delete()
        super(Progress, self).save(kwargs)


__all__ = ['Bookmark', 'UserProfile']
