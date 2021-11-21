"""API viewsets for the reader app."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Type
from warnings import filterwarnings

from django.db.models import Count, Max, Q
from django.utils import timezone as tz

from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin,
    RetrieveModelMixin, UpdateModelMixin
)
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from api.v2.mixins import CORSMixin
from api.v2.pagination import PageLimitPagination
from api.v2.schema import OpenAPISchema

from . import filters, models, serializers

if TYPE_CHECKING:  # pragma: no cover
    from django.db.models.query import QuerySet

# XXX: We are overriding the "Series" schema on purpose.
filterwarnings('ignore', '^Schema', module=OpenAPISchema.__base__.__module__)


class ArtistViewSet(CORSMixin, ModelViewSet):
    """
    API endpoints for artists.

    * list: List artists.
    * read: View a certain artist.
    * create: Create a new artist.
    * update: Edit the given artist.
    * patch: Patch the given artist.
    * delete: Delete the given artist.
    """
    schema = OpenAPISchema(tags=('artists',))
    queryset = models.Artist.objects.all()
    serializer_class = serializers.ArtistSerializer


class AuthorViewSet(CORSMixin, ModelViewSet):
    """
    API endpoints for authors.

    * list: List authors.
    * read: View a certain author.
    * create: Create a new author.
    * update: Edit the given author.
    * patch: Patch the given author.
    * delete: Delete the given author.
    """
    schema = OpenAPISchema(tags=('authors',))
    queryset = models.Author.objects.all()
    serializer_class = serializers.AuthorSerializer


class CategoryViewSet(CORSMixin, ModelViewSet):
    """
    API endpoints for categories.

    * list: List categories.
    * read: View a certain category.
    * create: Create a new category.
    * patch: Patch the given category.
    * delete: Delete the given category.
    """
    schema = OpenAPISchema(tags=('categories',), component_name='Category')
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all()
    lookup_field = 'name'


class PageViewSet(CreateModelMixin, DestroyModelMixin, ListModelMixin,
                  UpdateModelMixin, CORSMixin, GenericViewSet):
    """
    API endpoints for pages.

    * list: List a chapter's pages.
    * create: Create a new page.
    * update: Edit the given page.
    * delete: Delete the given page.
    """
    schema = OpenAPISchema(tags=('pages',),)
    http_method_names = ('get', 'post', 'put', 'delete', 'head', 'options')
    queryset = models.Page.objects.all()
    serializer_class = serializers.PageSerializer
    filter_backends = filters.PAGE_FILTERS


class ChapterViewSet(CORSMixin, ModelViewSet):
    """
    API endpoints for chapters.

    * list: List chapters.
    * read: View a certain chapter.
    * create: Create a new chapter.
    * update: Edit the given chapter.
    * patch: Patch the given chapter.
    * delete: Delete the given chapter.
    """
    schema = OpenAPISchema(tags=('chapters',))
    serializer_class = serializers.ChapterSerializer
    filter_backends = filters.CHAPTER_FILTERS

    def get_queryset(self) -> QuerySet:
        return models.Chapter.objects.select_related('series') \
            .filter(published__lte=tz.now()).order_by('-published')


class SeriesViewSet(CORSMixin, ModelViewSet):
    """
    API endpoints for series.

    * list: List or search for series.
    * read: View the details of a series.
    * create: Create a new series.
    * update: Edit the given series.
    * patch: Patch the given series.
    * delete: Delete the given series.
    """
    schema = OpenAPISchema(
        operation_id_base='Series',
        tags=('series',), component_name='Series'
    )
    filter_backends = filters.SERIES_FILTERS
    pagination_class = PageLimitPagination
    ordering = ('title',)
    lookup_field = 'slug'

    def get_queryset(self) -> QuerySet:
        q = Q(chapters__published__lte=tz.now())
        return models.Series.objects.prefetch_related('chapters').annotate(
            chapter_count=Count('chapters', filter=q),
            latest_upload=Max('chapters__published')
        ).filter(chapter_count__gt=0).distinct()

    def get_serializer_class(self) -> Type[serializers.SeriesSerializer]:
        return serializers.SeriesSerializer[self.action]


class CubariViewSet(RetrieveModelMixin, CORSMixin, GenericViewSet):
    """
    API endpoints for Cubari.

    * read: Generate JSON for a cubari.moe gist.
    """
    schema = OpenAPISchema(tags=('cubari',), operation_id_base='Cubari')
    queryset = models.Series.objects.all()
    serializer_class = serializers.CubariSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = 'slug'
    _restrict = True

    def get_permissions(self) -> List:
        if self.request.method == 'OPTIONS':
            return []
        return super().get_permissions()


__all__ = [
    'ArtistViewSet', 'AuthorViewSet', 'CategoryViewSet',
    'PageViewSet', 'ChapterViewSet', 'SeriesViewSet', 'CubariViewSet'
]
