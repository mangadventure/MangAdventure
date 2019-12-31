from re import match
from unittest.mock import MagicMock

from pytest import fixture, mark

from config.templatetags.custom_tags import (
    get_type, jsonld, order_by, urljoin, vslice
)
from reader.models import Series


def test_url_join():
    assert urljoin('https://origin', 'api/test') == 'https://origin/api/test'


def test_jsonld():
    value = {
        '@context': {
            'thing': '<iframe></>'
        },
        'thing': '&'
    }
    element_id = 'whatever'
    tag = jsonld(value, element_id)
    assert tag.startswith(f'<script id="{element_id}"')
    body = match(r"<script.*?>(.*?)</script>", tag).group(1)
    assert '<' not in body
    assert '>' not in body
    assert '&' not in body


def test_vslice():
    value = [1, 2, 3, 4, 5, 6]
    end = 3
    assert vslice(value, end) == [1, 2, 3]


@fixture
def mock_urlopen(monkeypatch):
    fake_urlopen = MagicMock()
    fake_urlopen().__enter__().info()\
        .get_content_type.return_value = 'image/jpeg'

    monkeypatch.setattr('config.templatetags.custom_tags.urlopen', fake_urlopen)


@mark.django_db
def test_order_by():
    Series.objects.create(title='d')
    Series.objects.create(title='a')
    qs = Series.objects.filter(title__in=['d', 'a'])
    ordered = order_by(qs, 'title')
    assert ordered[0].title == 'a'
    assert ordered[1].title == 'd'


def test_get_type(mock_urlopen):
    assert get_type('my_link.png') == 'image/jpeg'


def test_get_type_no_network():
    assert get_type("my_link.png") == 'image/png'


def test_get_type_invalid():
    assert get_type("whatever") == 'image/jpeg'
