from django.db import models
from django.contrib.auth.models import User
from reader.models import Series
from MangAdventure.utils import storage, uploaders, validators


class Bookmark(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bookmarks'
    )

    class Meta:
        unique_together = ('series', 'user')


class UserProfile(models.Model):
    _validator = validators.FileSizeValidator(max_mb=2)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(
        blank=True, verbose_name='biography',
        help_text="The user's biography."
    )
    avatar = models.ImageField(
        storage=storage.OverwriteStorage(),
        upload_to=uploaders.avatar_uploader,
        help_text="The user's avatar image. Must be "
                  "up to %d MBs." % _validator.max_mb,
        validators=[_validator], blank=True
    )
    bookmarks = models.ManyToManyField(
        Bookmark, related_name='bookmarks', blank=True,
        help_text="The user's bookmarked series."
    )
    
    def __str__(self): return str(self.user)


# TODO: add user preferences

__all__ = ['Bookmark', 'UserProfile']

