"""Custom authentication backends."""

from typing import TYPE_CHECKING, Any, Optional

from django.contrib.auth.backends import ModelBackend

if TYPE_CHECKING:  # pragma: no cover
    from django.contrib.auth.models import User


class ScanlationBackend(ModelBackend):
    """Authentication backend with scanlator permissions."""
    @staticmethod
    def is_scanlator(user_obj: 'User') -> bool:
        """
        Check whether the given user is a scanlator.

        :param user_obj: A ``User`` model instance.

        :return: ``True`` if the user is in the "Scanlator" group.
        """
        return user_obj.groups.filter(name='Scanlator').exists()

    def has_perm(self, user_obj: 'User', perm: str,
                 obj: Optional[Any] = None) -> bool:
        if not user_obj.is_active:
            return False
        if self.is_scanlator(user_obj):
            return getattr(obj, 'manager_id', -1) == user_obj.pk
        return super(ModelBackend, self).has_perm(user_obj, perm, obj=obj)


__all__ = ['ScanlationBackend']
