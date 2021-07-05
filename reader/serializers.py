"""Model serializers for the reader app."""

from typing import Dict, Generic, List, Type, TypeVar

from rest_framework.fields import CharField, SerializerMethodField, URLField
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
    series = SlugRelatedField(
        queryset=Series.objects.only('slug', 'title'),
        slug_field='slug', help_text='The series of the chapter.'
    )
    pages = SerializerMethodField(
        help_text='The pages of the chapter.', method_name='_get_pages'
    )
    groups = StringRelatedField(
        many=True, help_text='The scanlation groups of the chapter.'
    )
    url = URLField(
        source='get_absolute_url', read_only=True,
        help_text='The absolute URL of the chapter.'
    )

    def __uri(self, path: str) -> str:
        return self.context['view'].request.build_absolute_uri(path)

    def _get_pages(self, obj: Chapter) -> List[str]:
        return [self.__uri(p.image.url) for p in obj.pages.iterator()]

    class Meta:
        model = Chapter
        fields = (
            'id', 'title', 'number', 'volume', 'published', 'final',
            'series', 'pages', 'groups', 'full_title', 'url', 'file'
        )
        extra_kwargs = {
            'file': {'write_only': True}
        }


class PageSerializer(ModelSerializer):
    """Serializer for chapter pages."""
    chapter = PrimaryKeyRelatedField(
        queryset=Chapter.objects.all(),
        help_text="The ID of the page's chapter."
    )

    class Meta:
        model = Page
        fields = ('id', 'chapter', 'image', 'number')
        extra_kwargs = {
            'image': {'help_text': 'The image of the page.'},
            'number': {'help_text': 'The number of the page.'}
        }
        validators = (
            UniqueTogetherValidator(
                queryset=model.objects.all(),
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

    class Meta:
        model = Series
        fields = ('title', 'slug', 'url', 'cover')


class _SeriesDetailSerializer(ModelSerializer):
    """
    Serializer for series details.

    .. admonition:: TODO
       :class: warning

       Make M2M fields editable.
    """
    authors = StringRelatedField(
        many=True, required=False, help_text='The authors of the series.'
    )
    artists = StringRelatedField(
        many=True, required=False, help_text='The artists of the series.'
    )
    categories = StringRelatedField(
        many=True, required=False, help_text='The categories of the series.'
    )
    chapters = PrimaryKeyRelatedField(
        many=True, read_only=True, required=False,
        help_text='The chapter IDs of the series.'
    )
    url = URLField(
        source='get_absolute_url', read_only=True,
        help_text='The absolute URL of the series.'
    )

    def create(self, validated_data: Dict) -> Series:
        # manually set the manager to the current user
        return super().create({
            **validated_data,
            'manager_id': self.context['request'].user.id
        })

    class Meta:
        model = Series
        fields = (
            'title', 'slug', 'url', 'cover',
            'description', 'completed', 'format',
            'chapters', 'authors', 'artists', 'categories'
        )
        extra_kwargs = {
            'slug': {'write_only': True},
            'format': {
                'write_only': True,
                'default': 'Vol. {volume}, Ch. {number}: {title}'
            }
        }


#: A series serializer type.
TSerializer = TypeVar(
    'TSerializer',
    Type[_SeriesListSerializer],
    Type[_SeriesDetailSerializer]
)


class SeriesSerializer(Generic[TSerializer]):
    """Generic series serializer."""
    def __class_getitem__(cls, action: str) -> TSerializer:
        """
        Adapt the series schema based on the action.

        :param action: An API view action.

        :return: The actual type of the serializer.
        """
        if action == 'list':
            return _SeriesListSerializer
        return _SeriesDetailSerializer


class CubariSerializer(ModelSerializer):
    """Serializer for cubari.moe gists."""
    title = CharField(read_only=True)
    description = CharField(read_only=True)
    artist = SerializerMethodField(method_name='_get_artist')
    author = SerializerMethodField(method_name='_get_author')
    cover = SerializerMethodField(method_name='_get_cover')
    chapters = SerializerMethodField(method_name='_get_chapters')

    def __uri(self, path: str) -> str:
        return self.context['view'].request.build_absolute_uri(path)

    def _get_artist(self, obj: Series) -> str:
        return ', '.join(obj.artists.values_list('name', flat=True))

    def _get_author(self, obj: Series) -> str:
        return ', '.join(obj.authors.values_list('name', flat=True))

    def _get_cover(self, obj: Series) -> str:
        return self.__uri(obj.cover.url)

    def _get_chapters(self, obj: Series) -> Dict[str, Dict]:
        result = dict()
        chapters = obj.chapters.prefetch_related('groups__name', 'pages')
        for ch in chapters.order_by('volume', 'number').iterator():
            volume = 'Uncategorized' if ch.volume == 0 else str(ch.volume)
            groups = ch.groups.values_list('name', flat=True)
            pages = ch.pages.order_by('number')
            result[f'{ch.number:g}'] = {
                'title': ch.title,
                'volume': volume,
                'groups': {
                    ', '.join(groups): [
                        self.__uri(p.image.url) for p in pages.iterator()
                    ]
                },
                'latest_update': str(round(ch.modified.timestamp()))
            }
        return result

    class Meta:
        model = Series
        fields = (
            'title', 'description', 'author',
            'artist', 'cover', 'chapters'
        )


__all__ = [
    'ArtistSerializer', 'AuthorSerializer',
    'CategorySerializer', 'ChapterSerializer',
    'PageSerializer', 'SeriesSerializer',
    'CubariSerializer', 'TSerializer'
]
