from django.http import Http404
from django.shortcuts import render

from .models import Group, Member


def all_groups(request):
    return render(request, 'all_groups.html', {
        'groups': Group.objects.all()
    })


def group(request, g_id=0):
    try:
        g_id = int(g_id)
    except (ValueError, TypeError):
        raise Http404
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
