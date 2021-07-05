"""API viewsets for the groups app."""

from rest_framework.viewsets import ModelViewSet

from api.v2.schema import OpenAPISchema

from . import models, serializers


class GroupViewSet(ModelViewSet):
    """
    API endpoints for groups.

    * list: List groups.
    * read: View a certain group.
    * create: Create a new group.
    * patch: Patch the given group.
    * delete: Delete the given group.
    """
    schema = OpenAPISchema(tags=('groups',))
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer


__all__ = ['GroupViewSet']
