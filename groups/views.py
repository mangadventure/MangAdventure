"""The views of the users app."""

from typing import TYPE_CHECKING

from django.http import Http404
from django.shortcuts import render

from .models import Group, Member

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def all_groups(request: 'HttpRequest') -> 'HttpResponse':
    """
     View that serves a page with all the groups.

    :param request: The original request.

    :return: A response with the rendered ``all_groups.html`` template.
    """
    return render(request, 'all_groups.html', {
        'groups': Group.objects.all()
    })


def group(request: 'HttpRequest', g_id: int) -> 'HttpResponse':
    """
     View that serves a single group's page.

    :param request: The original request.
    :param g_id: The ID of the group.

    :return: A response with the rendered ``group.html`` template.

    :raises Http404: If the group does not exist.
    """
    if g_id == 0:
        raise Http404
    try:
        _group = Group.objects.get(id=g_id)
    except Group.DoesNotExist:
        raise Http404
    member_ids = []
    for role in _group.roles.values('member_id').distinct():
        member_ids.append(role['member_id'])
    members = Member.objects.filter(id__in=member_ids)
    return render(request, 'group.html', {
        'group': _group, 'members': members.order_by('name')
    })


__all__ = ['all_groups', 'group']
