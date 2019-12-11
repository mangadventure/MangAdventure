"""
Functions used for sorting.

.. seealso::

    https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/
"""

from re import split
from typing import List, Union


def atoi(s: str) -> Union[int, str]:
    """Convert a :class:`str` to an :class:`int` if possible."""
    return int(s) if s.isdigit() else s.lower()


def alnum_key(k: str) -> List[str]:
    """Generate an alphanumeric key for sorting."""
    return list(map(atoi, split('([0-9]+)', k)))


def natural_sort(original: List[str]) -> List[str]:
    """
    Sort a list in natural order.

    .. code-block:: python

       >>> sorted(map(str, range(12)))
       ['0', '1', '10', '11', '2', '3', '4', '5', '6', '7', '8', '9']
       >>> natural_sort(map(str, range(12)))
       ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']

    :param original: The original list.

    :return: The sorted list.
    """
    return sorted(original, key=alnum_key)


__all__ = ['natural_sort']
