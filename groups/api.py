"""API viewsets for the groups app."""

from rest_framework.viewsets import ModelViewSet

from api.v2.mixins import CORSMixin
from api.v2.schema import OpenAPISchema

from . import models, serializers


class GroupViewSet(CORSMixin, ModelViewSet):
    """
    API endpoints for groups.

    * list: List groups.
    * read: View a certain group.
    * create: Create a new group.
    * update: Edit the given author.
    * patch: Patch the given group.
    * delete: Delete the given group.
    """
    schema = OpenAPISchema(tags=('groups',))
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer


__all__ = ['GroupViewSet']
