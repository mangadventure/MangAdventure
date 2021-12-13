"""API viewsets for the groups app."""

from rest_framework.parsers import MultiPartParser
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
    * update: Update the given author.
    * patch: Edit the given group.
    * delete: Delete the given group.
    """
    schema = OpenAPISchema(tags=('groups',))
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer
    parser_classes = (MultiPartParser,)


__all__ = ['GroupViewSet']
