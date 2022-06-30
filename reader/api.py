"""API viewsets for the reader app."""

from __future__ import annotations

from typing import TYPE_CHECKING, Type
from warnings import filterwarnings

from django.db.models import Count, Max, Prefetch, Q, Sum
from django.utils import timezone as tz

from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin,
    RetrieveModelMixin, UpdateModelMixin
)
from rest_framework.parsers import MultiPartParser
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from api.v2.mixins import CORSMixin
from api.v2.pagination import PageLimitPagination
from api.v2.schema import OpenAPISchema
from groups.models import Group

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
    * update: Update the given artist.
    * patch: Edit the given artist.
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
    * update: Update the given author.
    * patch: Edit the given author.
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
    * patch: Edit the given category.
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
    * update: Update the given page.
    * patch: Edit the given page.
    * delete: Delete the given page.
    """
    schema = OpenAPISchema(tags=('pages',),)
    queryset = models.Page.objects.all()
    serializer_class = serializers.PageSerializer
    filter_backends = filters.PAGE_FILTERS
    parser_classes = (MultiPartParser,)


class ChapterViewSet(CORSMixin, ModelViewSet):
    """
    API endpoints for chapters.

    * list: List chapters.
    * read: View a certain chapter.
    * create: Create a new chapter.
    * update: Update the given chapter.
    * patch: Edit the given chapter.
    * delete: Delete the given chapter.
    """
    schema = OpenAPISchema(tags=('chapters',))
    serializer_class = serializers.ChapterSerializer
    filter_backends = filters.CHAPTER_FILTERS
    parser_classes = (MultiPartParser,)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        if instance.series.licensed:
            raise _LegalException()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self) -> QuerySet:
        return models.Chapter.objects.select_related('series') \
            .filter(published__lte=tz.now()).order_by('-published')


class SeriesViewSet(CORSMixin, ModelViewSet):
    """
    API endpoints for series.

    * list: List or search for series.
    * read: View the details of a series.
    * create: Create a new series.
    * update: Update the given series.
    * patch: Edit the given series.
    * delete: Delete the given series.
    """
    schema = OpenAPISchema(
        operation_id_base='Series',
        tags=('series',), component_name='Series'
    )
    filter_backends = filters.SERIES_FILTERS
    parser_classes = (MultiPartParser,)
    pagination_class = PageLimitPagination
    ordering = ('title',)
    lookup_field = 'slug'

    def get_queryset(self) -> QuerySet:
        q = Q(chapters__published__lte=tz.now())
        return models.Series.objects.annotate(
            chapter_count=Count('chapters', filter=q),
            latest_upload=Max('chapters__published'),
            views=Sum('chapters__views', distinct=True)
        ).filter(chapter_count__gt=0).distinct()

    def get_serializer_class(self) -> Type[serializers.SeriesSerializer]:
        return serializers.SeriesSerializer[self.action]


class CubariViewSet(RetrieveModelMixin, CORSMixin, GenericViewSet):
    """
    API endpoints for Cubari.

    * read: Generate JSON for cubari.moe.
    """
    schema = OpenAPISchema(tags=('cubari',), operation_id_base='Cubari')
    serializer_class = serializers.CubariSerializer
    lookup_field = 'slug'

    def get_queryset(self) -> QuerySet:
        pages = models.Page.objects.order_by('number')
        groups = Group.objects.only('name')
        chapters = models.Chapter.objects.prefetch_related(
            Prefetch('pages', queryset=pages),
            Prefetch('groups', queryset=groups)
        ).order_by('volume', 'number').only(
            'title', 'number', 'volume', 'modified', 'series'
        )
        return models.Series.objects.defer(
            'manager_id', 'modified',
            'created', 'completed', 'licensed'
        ).prefetch_related(
            Prefetch('authors'), Prefetch('artists'),
            Prefetch('chapters', queryset=chapters)
        )


__all__ = [
    'ArtistViewSet', 'AuthorViewSet', 'CategoryViewSet',
    'PageViewSet', 'ChapterViewSet', 'SeriesViewSet', 'CubariViewSet'
]
