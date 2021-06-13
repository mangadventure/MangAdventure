"""The views of the users app."""

from typing import TYPE_CHECKING

from django.http import Http404
from django.shortcuts import render
from django.views.decorators.cache import cache_control

from MangAdventure.jsonld import breadcrumbs

from .models import Group

if TYPE_CHECKING:  # pragma: no cover
    from django.http import HttpRequest, HttpResponse


@cache_control(max_age=7200)
def all_groups(request: 'HttpRequest') -> 'HttpResponse':
    """
     View that serves a page with all the groups.

    :param request: The original request.

    :return: A response with the rendered ``all_groups.html`` template.
    """
    uri = request.build_absolute_uri(request.path)
    crumbs = breadcrumbs([('Groups', uri)])
    return render(request, 'all_groups.html', {
        'groups': Group.objects.all(),
        'breadcrumbs': crumbs
    })


@cache_control(max_age=7200)
def group(request: 'HttpRequest', g_id: int) -> 'HttpResponse':
    """
     View that serves a single group's page.

    :param request: The original request.
    :param g_id: The ID of the group.

    :return: A response with the rendered ``group.html`` template.

    :raises Http404: If the group does not exist.
    """
    if g_id == 0:
        raise Http404('Group ID cannot be 0')
    try:
        _group = Group.objects.get(id=g_id)
    except Group.DoesNotExist as e:
        raise Http404 from e
    members = _group.members.distinct()
    url = request.path
    p_url = url.rsplit('/', 2)[0] + '/'
    crumbs = breadcrumbs([
        ('Groups', request.build_absolute_uri(p_url)),
        (_group.name, request.build_absolute_uri(url))
    ])
    return render(request, 'group.html', {
        'group': _group,
        'members': members.order_by('name'),
        'breadcrumbs': crumbs
    })


__all__ = ['all_groups', 'group']
