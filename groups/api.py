"""API viewsets for the groups app."""

from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control

from rest_framework.parsers import MultiPartParser
from rest_framework.viewsets import ModelViewSet

from api.v2.mixins import METHODS, CORSMixin
from api.v2.schema import OpenAPISchema

from . import models, serializers


@method_decorator(cache_control(public=True, max_age=7200), 'dispatch')
class GroupViewSet(CORSMixin, ModelViewSet):
    """
    API endpoints for groups.

    * list: List groups.
    * read: View a certain group.
    * create: Create a new group.
    * patch: Edit the given group.
    * delete: Delete the given group.
    """
    schema = OpenAPISchema(tags=('groups',))
    queryset = models.Group.objects.prefetch_related(
        Prefetch('roles', queryset=(
            models.Role.objects.only(
                'member__name', 'role', 'group_id'
            ).select_related('member')
        ))
    )
    serializer_class = serializers.GroupSerializer
    parser_classes = (MultiPartParser,)
    http_method_names = METHODS


@method_decorator(cache_control(public=True, max_age=10800), 'dispatch')
class MemberViewSet(CORSMixin, ModelViewSet):
    """
    API endpoints for members.

    * list: List members.
    * read: View a certain member.
    * create: Create a new member.
    * patch: Edit the given member.
    * delete: Delete the given member.
    """
    schema = OpenAPISchema(tags=('members',))
    queryset = models.Member.objects.prefetch_related(
        Prefetch('roles', queryset=(
            models.Role.objects.only('role', 'group_id')
        ))
    )
    serializer_class = serializers.MemberSerializer
    parser_classes = (MultiPartParser,)
    http_method_names = METHODS


__all__ = ['GroupViewSet', 'MemberViewSet']
