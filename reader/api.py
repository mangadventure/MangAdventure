"""API viewsets for the reader app."""

from __future__ import annotations

from typing import TYPE_CHECKING
from warnings import filterwarnings

from django.db.models import Count, F, Max, Prefetch, Q, Sum
from django.utils import timezone as tz
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control

from rest_framework.decorators import action
from rest_framework.exceptions import APIException, NotFound, ParseError
from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin,
    RetrieveModelMixin, UpdateModelMixin
)
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from api.v2.mixins import METHODS, CORSMixin
from api.v2.pagination import DummyPagination, PageLimitPagination
from api.v2.schema import OpenAPISchema
from groups.models import Group

from . import filters, models, serializers

if TYPE_CHECKING:  # pragma: no cover
    from django.db.models.query import QuerySet  # isort:skip
    from rest_framework.request import Request  # isort:skip

# XXX: We are overriding the "Series" schema on purpose.
filterwarnings('ignore', '^Schema', module=OpenAPISchema.__base__.__module__)


class _LegalException(APIException):
    status_code = 451
    default_detail = 'This series is licensed.'
    default_code = 'licensed_series'


@method_decorator(cache_control(public=True, max_age=1800), 'dispatch')
class ArtistViewSet(CORSMixin, ModelViewSet):
    """
    API endpoints for artists.

    * list: List artists.
    * read: View a certain artist.
    * create: Create a new artist.
    * patch: Edit the given artist.
    * delete: Delete the given artist.
    """
    schema = OpenAPISchema(tags=('artists',))
    queryset = models.Artist.objects.all()
    serializer_class = serializers.ArtistSerializer
    http_method_names = METHODS


@method_decorator(cache_control(public=True, max_age=1800), 'dispatch')
class AuthorViewSet(CORSMixin, ModelViewSet):
    """
    API endpoints for authors.

    * list: List authors.
    * read: View a certain author.
    * create: Create a new author.
    * patch: Edit the given author.
    * delete: Delete the given author.
    """
    schema = OpenAPISchema(tags=('authors',))
    queryset = models.Author.objects.all()
    serializer_class = serializers.AuthorSerializer
    http_method_names = METHODS


@method_decorator(cache_control(public=True, max_age=900), 'dispatch')
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
    serializer_class = serializers.CategorySerializer
    filter_backends = filters.CATEGORY_FILTERS
    queryset = models.Category.objects.all()
    lookup_field = 'name'
    http_method_names = METHODS


@method_decorator(cache_control(public=True, max_age=600), 'dispatch')
class PageViewSet(CreateModelMixin, DestroyModelMixin, ListModelMixin,
                  UpdateModelMixin, CORSMixin, GenericViewSet):
    """
    API endpoints for pages.

    * list: List a chapter's pages.
    * create: Create a new page.
    * patch: Edit the given page.
    * delete: Delete the given page.
    """
    schema = OpenAPISchema(tags=('pages',),)
    queryset = models.Page.objects.all()
    serializer_class = serializers.PageSerializer
    filter_backends = filters.PAGE_FILTERS
    parser_classes = (MultiPartParser,)
    http_method_names = METHODS


@method_decorator(cache_control(public=True, max_age=600), 'dispatch')
class ChapterViewSet(CORSMixin, ModelViewSet):
    """
    API endpoints for chapters.

    * list: List chapters.
    * read: View a certain chapter.
    * create: Create a new chapter.
    * patch: Edit the given chapter.
    * delete: Delete the given chapter.
    """
    schema = OpenAPISchema(tags=('chapters',))
    serializer_class = serializers.ChapterSerializer
    filter_backends = filters.CHAPTER_FILTERS
    parser_classes = (MultiPartParser,)
    http_method_names = METHODS

    @action(methods=['get'], detail=True, name='Chapter Pages',
            serializer_class=serializers.PageSerializer,
            pagination_class=DummyPagination,
            filter_backends=[filters.TrackingFilter])
    def pages(self, request: Request, pk: int) -> Response:
        """Get the pages of the chapter."""
        try:
            instance = models.Chapter.objects.filter(
                published__lte=tz.now()
            ).select_related('series').only(
                'series__slug', 'volume',
                'series__licensed', 'number'
            ).prefetch_related('pages').get(id=pk)
        except ValueError:
            raise ParseError()
        except models.Chapter.DoesNotExist:
            raise NotFound()
        if instance.series.licensed:
            raise _LegalException()
        serializer = serializers.PageSerializer(
            instance.pages.all(), many=True,
            context=self.get_serializer_context()
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['get'], detail=True, name='Read Chapter')
    def read(self, request: Request, pk: int) -> Response:
        """Redirect to the reader."""
        try:
            instance = models.Chapter.objects.filter(
                published__lte=tz.now()
            ).select_related('series').only(
                'series__slug', 'volume',
                'series__licensed', 'number'
            ).get(id=pk)
        except ValueError:
            raise ParseError()
        except models.Chapter.DoesNotExist:
            raise NotFound()
        if instance.series.licensed:
            raise _LegalException()
        url = request.build_absolute_uri(instance.get_absolute_url())
        return Response(status=308, headers={'Location': url})

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        if instance.series.licensed:
            raise _LegalException()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self) -> QuerySet:
        return models.Chapter.objects.select_related('series') \
            .filter(published__lte=tz.now()).order_by('-published')


@method_decorator(cache_control(public=True, max_age=300), 'dispatch')
class SeriesViewSet(CORSMixin, ModelViewSet):
    """
    API endpoints for series.

    * list: List or search for series.
    * read: View the details of a series.
    * create: Create a new series.
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
    http_method_names = METHODS

    @action(methods=['get'], detail=True, name='Series Chapters',
            serializer_class=serializers.ChapterSerializer,
            pagination_class=DummyPagination,
            filter_backends=[filters.DateFormat])
    def chapters(self, request: Request, slug: str) -> Response:
        """Get the chapters of the series."""
        try:
            now = tz.now()
            groups = Group.objects.only('name')
            chapters = models.Chapter.objects.filter(
                published__lte=now
            ).order_by('-published')
            instance = models.Series.objects.annotate(
                chapter_count=Count('chapters', filter=Q(
                    chapters__published__lte=now
                )),
            ).filter(chapter_count__gt=0).prefetch_related(
                Prefetch('chapters', queryset=chapters),
                Prefetch('chapters__groups', queryset=groups)
            ).only('title', 'slug').get(slug=slug)
        except models.Series.DoesNotExist:
            raise NotFound()
        if instance.licensed:
            raise _LegalException()
        serializer = serializers.ChapterSerializer(
            instance.chapters.all(), many=True,
            context=self.get_serializer_context()
        )
        return self.get_paginated_response(serializer.data)

    def get_queryset(self) -> QuerySet:
        q = Q(chapters__published__lte=tz.now())
        return models.Series.objects.annotate(
            chapter_count=Count('chapters', filter=q),
            latest_upload=Max('chapters__published', filter=q),
            views=Sum('chapters__views', distinct=True)
        ).filter(chapter_count__gt=0).distinct()

    def get_serializer_class(self) -> type[serializers.SeriesSerializer]:
        return serializers.SeriesSerializer[self.action]  # type: ignore


@method_decorator(cache_control(public=True, max_age=600), 'dispatch')
class CubariViewSet(RetrieveModelMixin, CORSMixin, GenericViewSet):
    """
    API endpoints for Cubari.

    * read: Generate JSON for cubari.moe.
    """
    schema = OpenAPISchema(tags=('cubari',), operation_id_base='Cubari')
    serializer_class = serializers.CubariSerializer
    lookup_field = 'slug'
    http_method_names = ['get', 'head', 'options']

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        if instance.licensed:
            raise _LegalException()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self) -> QuerySet:
        pages = models.Page.objects.order_by('number')
        groups = Group.objects.only('name')
        chapters = models.Chapter.objects.prefetch_related(
            Prefetch('pages', queryset=pages),
            Prefetch('groups', queryset=groups)
        ).filter(published__lte=tz.now()).order_by(
            F('volume').asc(nulls_last=True), 'number'
        ).only('id', 'title', 'number', 'volume', 'modified', 'series_id')
        return models.Series.objects.defer(
            'manager_id', 'modified', 'created', 'status'
        ).prefetch_related(
            Prefetch('chapters', queryset=chapters),
            Prefetch('authors'), Prefetch('artists')
        )


__all__ = [
    'ArtistViewSet', 'AuthorViewSet', 'CategoryViewSet',
    'PageViewSet', 'ChapterViewSet', 'SeriesViewSet', 'CubariViewSet'
]
