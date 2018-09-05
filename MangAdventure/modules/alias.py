from django.db import models


class Alias(models.Model):
    alias = None

    class Meta:
        abstract = True
        verbose_name = 'alias'
        verbose_name_plural = verbose_name + 'es'

    def __str__(self): return self.alias


def alias_field(help_text, max_length=100):
    return models.CharField(max_length=max_length, blank=True,
                            help_text=help_text, unique=True)


def foreign_key(cls):
    return models.ForeignKey(cls, related_name='aliases',
                             on_delete=models.CASCADE)


__all__ = ['Alias', 'alias_field', 'foreign_key']

