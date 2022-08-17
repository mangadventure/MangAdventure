"""Template tags of the groups app."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.defaultfilters import register

if TYPE_CHECKING:  # pragma: no cover
    from groups.models import Group, Member


@register.filter
def group_roles(member: Member, group: Group) -> str:
    """
    Get the roles of the member within the group.

    :param member: A ``Member`` model instance.
    :param group: A ``Group`` model instance.

    :return: A comma-separated list of roles.
    """
    return member.get_roles(group) or 'N/A'


__all__ = ['group_roles']
