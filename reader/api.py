"""API viewsets for the reader app."""

from typing import List
from warnings import filterwarnings

from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from api.v2.schema import OpenAPISchema

from . import models, serializers

# XXX: We are overriding the "Series" schema on purpose.
filterwarnings('ignore', '^Schema', module=OpenAPISchema.__base__.__module__)


class ArtistViewSet(ModelViewSet):
    """API endpoints for artists."""
    schema = OpenAPISchema(tags=('artists',))
    queryset = models.Artist.objects.all()
    serializer_class = serializers.ArtistSerializer


class AuthorViewSet(ModelViewSet):
    """
    API endpoints for authors.

    * list: List authors.
    * read: View a certain author.
    * create: Create a new author.
    * patch: Patch the given author.
    * delete: Delete the given author.
    """
    schema = OpenAPISchema(tags=('authors',))
    queryset = models.Author.objects.all()
    serializer_class = serializers.AuthorSerializer


class CategoryViewSet(ModelViewSet):
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


class PageViewSet(ModelViewSet):
    """
    API endpoints for pages.

    * create: Create a new page.
    * update: Edit the given page.
    * delete: Delete the given page.
    """
    schema = OpenAPISchema(tags=('pages',),)
    http_method_names = ('post', 'put', 'delete', 'head', 'options')
    queryset = models.Page.objects.all()
    serializer_class = serializers.PageSerializer


class ChapterViewSet(ModelViewSet):
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
    queryset = models.Chapter.objects.all()
    serializer_class = serializers.ChapterSerializer


class SeriesViewSet(ModelViewSet):
    """
    API endpoints for series.

    * list: List or search for series.
    * read: View the details of a series.
    * create: Create a new series.
    * update: Edit the given series.
    * patch: Patch the given series.
    * delete: Delete the given series.
    """
    schema = OpenAPISchema(tags=('series',), component_name='Series')
    queryset = models.Series.objects.order_by('id')
    lookup_field = 'slug'

    def get_serializer_class(self) -> serializers.TSerializer:
        # explicit call until we drop Python 3.6 in v0.8
        return serializers.SeriesSerializer.__class_getitem__(self.action)


class CubariViewSet(RetrieveModelMixin, GenericViewSet):
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
