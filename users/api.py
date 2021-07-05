"""API viewsets for the users app."""

from typing import TYPE_CHECKING, List

from django.urls import reverse

from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from api.v2.schema import OpenAPISchema

from .models import ApiKey, UserProfile
from .serializers import (
    BookmarkPagination, BookmarkSerializer, ProfileSerializer
)

if TYPE_CHECKING:  # pragma: no cover
    from django.db.models import QuerySet  # isort:skip
    from rest_framework.request import Request  # isort:skip


class BookmarkViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                      mixins.DestroyModelMixin, GenericViewSet):
    """
    API endpoints for bookmarks.

    * list: List your bookmarked series and the feed URLs.
    * create: Bookmark the given series.
    * delete: Unbookmark the given series.
    """
    schema = OpenAPISchema(tags=('bookmarks',))
    permission_classes = (IsAuthenticated,)
    serializer_class = BookmarkSerializer
    pagination_class = BookmarkPagination
    lookup_field = 'series__slug'
    lookup_url_kwarg = 'slug'
    _restrict = True

    def get_permissions(self) -> List:
        if self.request.method == 'OPTIONS':
            return []
        return super().get_permissions()

    def get_queryset(self) -> 'QuerySet':
        return self.request.user.bookmarks.all()

    def list(self, request: 'Request', *args, **kwargs) -> Response:
        token = request.user.profile.token
        rss = request.build_absolute_uri(
            reverse('user_bookmarks.rss') + '?token=' + token
        )
        atom = request.build_absolute_uri(
            reverse('user_bookmarks.atom') + '?token=' + token
        )
        bookmarks = self.get_serializer(self.get_queryset(), many=True).data
        return Response({'rss': rss, 'atom': atom, 'bookmarks': bookmarks})


class ProfileViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin, GenericViewSet):
    """
    API endpoints for user profiles.

    * read: View your profile.
    * update: Edit your profile.
    * patch: Patch your profile.
    * delete: Delete your profile.
    """
    schema = OpenAPISchema(tags=('profile',))
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
    lookup_field = None
    _restrict = True

    def get_permissions(self) -> List:
        if self.request.method == 'OPTIONS':
            return []
        return super().get_permissions()

    def get_object(self) -> UserProfile:
        return UserProfile.objects.select_related('user') \
            .get_or_create(user_id=self.request.user.id)[0]

    def perform_update(self, serializer: ProfileSerializer):
        data = dict(serializer.validated_data)
        fields = data.pop('user', {})
        profile = serializer.instance
        user = profile.user
        if fields:  # update the underlying user first
            for k, v in fields.items():
                setattr(user, k, v)
            user.save(update_fields=list(fields))
        if data:  # and then update the profile
            for k, v in data.items():
                setattr(profile, k, v)
            profile.save(update_fields=list(data))

    def perform_destroy(self, instance: UserProfile):
        # deactivate and anonymize the user
        instance.user.is_active = False
        instance.user.first_name = ''
        instance.user.last_name = ''
        instance.user.api_key.delete()
        instance.user.save(update_fields=(
            'is_active', 'first_name', 'last_name'
        ))
        instance.delete()

    @classmethod
    def as_view(cls, **initkwargs):
        return super().as_view(actions={
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
            'options': 'options'
        }, **initkwargs)


class ApiKeyViewSet(mixins.CreateModelMixin, GenericViewSet):
    """
    API endpoints for API keys.

    * create: Create or retrieve your API key.
    """
    schema = OpenAPISchema(
        operation_id_base='ApiKey',
        tags=('token',), component_name='ApiKey'
    )
    serializer_class = AuthTokenSerializer
    permission_classes = ()

    def create(self, request: 'Request', *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = ApiKey.objects.get_or_create(user=user)
        return Response({'token': token.key}, 201 if created else 200)


__all__ = ['BookmarkViewSet', 'ApiKeyViewSet']
