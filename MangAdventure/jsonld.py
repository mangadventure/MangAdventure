"""
Functions used to generate JSON-LD_ objects.

.. _JSON-LD: https://json-ld.org/
"""

from typing import Any, Dict, List, Tuple

JSON = Dict[str, Any]


def schema(at_type: str, items: JSON) -> JSON:
    """
    Generate an arbitrary JSON-LD object.

    The object's ``@context`` links to https://schema.org.

    :param at_type: The ``@type`` of the object.
    :param items: The key-value pairs of the object.

    :return: A JSON-LD dictionary.
    """
    return {
        '@context': 'https://schema.org',
        '@type': at_type, **items
    }


def breadcrumbs(items: List[Tuple[str, str]]) -> JSON:
    """
    Generate a :schema:`BreadcrumbList` JSON-LD object.

    :param items: A list of :schema:`ListItem` tuples. The first
                  element of each tuple is the :schema:`name`
                  and the second is the :schema:`item`.

    :return: A JSON-LD dictionary.

    .. seealso:
        https://developers.google.com/search/docs/data-types/breadcrumb
    """
    return schema('BreadcrumbList', {
        'itemListElement': [{
            '@type': 'ListItem',
            'position': pos,
            'name': name,
            'item': item
        } for pos, (name, item) in enumerate(items, 1)]
    })


def carousel(items: List[str]) -> JSON:
    """
    Generate an :schema:`ItemList` JSON-LD object.

    :param items: A list of :schema:`ListItem` :schema:`urls <url>`

    :return: A JSON-LD dictionary.

    .. seealso:
        https://developers.google.com/search/docs/data-types/carousel
    """
    return schema('ItemList', {
        'itemListElement': [{
            '@type': 'ListItem',
            'position': pos,
            'url': url
        } for pos, url in enumerate(items, 1)]
    })


__all__ = ['schema', 'breadcrumbs', 'carousel']
