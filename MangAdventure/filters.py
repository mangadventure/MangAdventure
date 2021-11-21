"""
A collection of filters used in the admin interface.

.. seealso:: :attr:`django.contrib.admin.ModelAdmin.list_filter`
"""

from functools import partial
from typing import Tuple, Type

from django.contrib.admin.filters import (
    FieldListFilter, RelatedFieldListFilter, SimpleListFilter
)


def title_filter(title: str, klass: Type[FieldListFilter] =
                 FieldListFilter) -> Type[FieldListFilter]:
    """
    A :class:`FieldListFilter` with a custom title.

    :param title: The title of the filter.
    :param klass: The parent class of the filter.
                  Must be a subclass of :class:`FieldListFilter`.

    :return: A class that inherits from ``klass``.
    """
    class _GenericFilter(klass):  # pragma: no cover
        def __new__(cls, *args, **kwargs):
            instance = super().create(*args, **kwargs)
            instance.title = title
            return instance

    return _GenericFilter


def boolean_filter(title: str, param: str, names:
                   Tuple[str, str]) -> Type[SimpleListFilter]:
    """
    A boolean :class:`SimpleListFilter`.

    :param title: The title of the filter.
    :param param: The name of the parameter to filter.
    :param names: The names for ``True`` and ``False`` respectively.

    :return: A class that inherits from :class:`SimpleListFilter`.
    """
    class _BooleanFilter(SimpleListFilter):  # pragma: no cover
        def __init__(self, *args, **kwargs):
            self.names = names
            self.title = title
            self.parameter_name = param
            super().__init__(*args, **kwargs)

        def lookups(self, request, model_admin):
            return [
                (True, self.names[0]),
                (False, self.names[1])
            ]

        def queryset(self, request, queryset):
            return {
                'True': queryset.filter(**{self.parameter_name: True}),
                'False': queryset.filter(**{self.parameter_name: False})
            }.get(self.value(), queryset)

    return _BooleanFilter


related_filter = partial(title_filter, klass=RelatedFieldListFilter)
related_filter.__doc__ = """
A :func:`title_filter` for related fields.

:return: A class that inherits from :class:`RelatedFieldListFilter`.
"""

__all__ = ['title_filter', 'boolean_filter', 'related_filter']
