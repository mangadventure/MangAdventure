from functools import partial

from django.contrib.admin import (
    FieldListFilter, RelatedFieldListFilter, SimpleListFilter
)


def title_filter(title, klass=FieldListFilter):
    class Wrapper(klass):
        def __new__(cls, *args, **kwargs):
            instance = super(Wrapper, cls).create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


def boolean_filter(title, param, names):
    class Wrapper(SimpleListFilter):
        def __init__(self, *args, **kwargs):
            self.names = names
            self.title = title
            self.parameter_name = param
            super(Wrapper, self).__init__(*args, **kwargs)

        def lookups(self, request, model_admin):
            return (
                (True, self.names[0]),
                (False, self.names[1])
            )

        def queryset(self, request, queryset):
            return {
                'True': queryset.filter(**{self.parameter_name: True}),
                'False': queryset.filter(**{self.parameter_name: False})
            }.get(self.value(), queryset)

    return Wrapper


related_filter = partial(title_filter, klass=RelatedFieldListFilter)


__all__ = ['title_filter', 'boolean_filter', 'related_filter']
