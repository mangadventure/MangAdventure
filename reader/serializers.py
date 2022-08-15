"""Model serializers for the reader app."""

from typing import Dict, Generic, List, Optional, Type, TypeVar

from django.db.models import F

from rest_framework.fields import (
    CharField, DateTimeField, IntegerField, SerializerMethodField, URLField
)
from rest_framework.relations import (
    PrimaryKeyRelatedField, SlugRelatedField, StringRelatedField
)
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator

from .models import Artist, Author, Category, Chapter, Page, Series


class ArtistSerializer(ModelSerializer):
    """Serializer for artists."""
    class Meta:
        model = Artist
        fields = ('id', 'name')
        read_only_fields = ('id',)


class AuthorSerializer(ModelSerializer):
    """Serializer for authors."""
    class Meta:
        model = Author
        fields = ('id', 'name')
        read_only_fields = ('id',)


class CategorySerializer(ModelSerializer):
    """Serializer for categories."""
    class Meta:
        model = Category
        fields = ('name', 'description')


class ChapterSerializer(ModelSerializer):
    """Serializer for chapters."""
    full_title = CharField(
        source='__str__', read_only=True,
        help_text='The formatted title of the chapter.'
    )
    views = IntegerField(
        min_value=0, read_only=True,
        help_text='The total views of the chapter.'
    )
    series = SlugRelatedField(
        queryset=Series.objects.only('slug', 'title'),
        slug_field='slug', help_text='The series of the chapter.'
    )
    groups = StringRelatedField(
        many=True, help_text='The scanlation groups of the chapter.'
    )  # type: StringRelatedField
    url = URLField(
        source='get_absolute_url', read_only=True,
        help_text='The absolute URL of the chapter.'
    )

    def to_representation(self, instance: Chapter) -> Dict:
        rep = super().to_representation(instance)
        # HACK: adapt the date format based on a query param
        dt_format = self.context['request'] \
            .query_params.get('date_format', 'iso-8601')
        published = instance.published
        rep['published'] = {
            'iso-8601': published.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'rfc-5322': published.strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'timestamp': str(round(published.timestamp() * 1e3))
        }.get(dt_format)
        return rep

    def __uri(self, path: str) -> str:
        return self.context['view'].request.build_absolute_uri(path)

    def _get_pages(self, obj: Chapter) -> List[str]:
        return [self.__uri(p.image.url) for p in obj.pages.iterator()]

    class Meta:
        model = Chapter
        fields = (
            'id', 'title', 'number', 'volume', 'published', 'views',
            'final', 'series', 'groups', 'full_title', 'url', 'file'
        )
        extra_kwargs = {
            'file': {'write_only': True}
        }


class PageSerializer(ModelSerializer):
    """Serializer for chapter pages."""
    chapter = PrimaryKeyRelatedField(
        help_text="The ID of the page's chapter.",
        queryset=Chapter.objects.order_by(
            'series', F('volume').asc(nulls_last=True), 'number'
        ), write_only=True
    )
    url = URLField(
        source='get_absolute_url', read_only=True,
        help_text='The absolute URL of the page.'
    )

    class Meta:
        model = Page
        fields = ('id', 'chapter', 'image', 'number', 'url')
        extra_kwargs = {
            'image': {'help_text': 'The image of the page.'},
            'number': {'help_text': 'The number of the page.'}
        }
        validators = (
            UniqueTogetherValidator(
                queryset=Page.objects.all(),
                fields=('chapter', 'number'),
                message='The chapter already has a page with this number.'
            ),
        )


class _SeriesListSerializer(ModelSerializer):
    """Serializer for series lists."""
    url = URLField(
        source='get_absolute_url', read_only=True,
        help_text='The absolute URL of the series.'
    )
    updated = DateTimeField(
        source='latest_upload', read_only=True,
        help_text='The latest chapter upload date.'
    )
    chapters = SerializerMethodField(
        method_name='_get_chapters', allow_null=True,
        help_text='The number of chapters or null if licensed.'
    )

    def _get_chapters(self, obj: Series) -> Optional[int]:
        return None if obj.licensed else getattr(obj, 'chapter_count')

    class Meta:
        model = Series
        fields = (
            'slug', 'title', 'url',
            'cover', 'updated', 'chapters'
        )


class _SeriesDetailSerializer(ModelSerializer):
    """
    Serializer for series details.

    .. admonition:: TODO
       :class: warning

       Make M2M fields editable.
    """
    updated = DateTimeField(
        source='latest_upload', read_only=True,
        help_text='The latest chapter upload date.'
    )
    views = IntegerField(
        min_value=0, read_only=True,
        help_text='The total chapter views of the series.'
    )
    aliases = StringRelatedField(
        many=True, required=False,
        help_text='The alternative titles of the series.'
    )  # type: StringRelatedField
    authors = StringRelatedField(
        many=True, required=False,
        help_text='The authors of the series.'
    )  # type: StringRelatedField
    artists = StringRelatedField(
        many=True, required=False,
        help_text='The artists of the series.'
    )  # type: StringRelatedField
    categories = StringRelatedField(
        many=True, required=False,
        help_text='The categories of the series.'
    )  # type: StringRelatedField
    url = URLField(
        source='get_absolute_url', read_only=True,
        help_text='The absolute URL of the series.'
    )

    def create(self, validated_data: Dict) -> Series:
        """Create a new ``Series`` instance."""
        # manually set the manager to the current user
        return super().create({
            **validated_data,
            'manager_id': self.context['request'].user.id
        })

    class Meta:
        model = Series
        fields = (
            'slug', 'title', 'url', 'cover', 'updated',
            'description', 'views', 'completed', 'licensed',
            'format', 'aliases', 'authors', 'artists', 'categories'
        )
        extra_kwargs = {
            'format': {
                'write_only': True,
                'default': 'Vol. {volume}, Ch. {number}: {title}'
            }
        }


#: A series serializer type.
TSeriesSerializer = TypeVar(
    'TSeriesSerializer',
    Type[_SeriesListSerializer],
    Type[_SeriesDetailSerializer]
)


class SeriesSerializer(Generic[TSeriesSerializer]):
    """Generic series serializer."""
    def __class_getitem__(cls, action: str) -> TSeriesSerializer:
        """
        Adapt the series schema based on the action.

        :param action: An API view action.

        :return: The actual type of the serializer.
        """
        if action == 'list':
            return _SeriesListSerializer  # type: ignore
        return _SeriesDetailSerializer  # type: ignore


class CubariSerializer(ModelSerializer):
    """Serializer for cubari.moe."""
    title = CharField(read_only=True)
    description = CharField(read_only=True)
    original_url = URLField(source='get_absolute_url', read_only=True)
    artist = SerializerMethodField(method_name='_get_artist')
    author = SerializerMethodField(method_name='_get_author')
    cover = SerializerMethodField(method_name='_get_cover')
    alt_titles = SerializerMethodField(method_name='_get_aliases')
    metadata = SerializerMethodField(method_name='_get_metadata')
    chapters = SerializerMethodField(method_name='_get_chapters')

    def __uri(self, path: str) -> str:
        return self.context['view'].request.build_absolute_uri(path)

    def _get_artist(self, obj: Series) -> str:
        return ', '.join(a.name for a in obj.artists.all())

    def _get_author(self, obj: Series) -> str:
        return ', '.join(a.name for a in obj.authors.all())

    def _get_cover(self, obj: Series) -> str:
        return self.__uri(obj.cover.url)

    def _get_aliases(self, obj: Series) -> List[str]:
        return obj.aliases.names()

    def _get_metadata(self, obj: Series) -> List[List[str]]:
        return [
            ['Author', self._get_author(obj)],
            ['Artist', self._get_artist(obj)]
        ]

    def _get_chapters(self, obj: Series) -> Dict[str, Dict]:
        return {
            f'{ch.number:g}': {
                'title': ch.title,
                'volume': str(ch.volume),
                'groups': {
                    ', '.join(g.name for g in ch.groups.all()) or 'N/A':
                    [self.__uri(p.image.url) for p in ch.pages.all()]
                },
                'last_updated': str(round(ch.modified.timestamp()))
            } for ch in obj.chapters.all()
        }

    class Meta:
        model = Series
        fields = (
            'title', 'cover', 'original_url', 'description',
            'author', 'artist', 'alt_titles', 'metadata', 'chapters'
        )


__all__ = [
    'ArtistSerializer', 'AuthorSerializer',
    'CategorySerializer', 'ChapterSerializer',
    'PageSerializer', 'SeriesSerializer', 'CubariSerializer'
]
