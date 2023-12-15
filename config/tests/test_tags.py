from re import match
from unittest.mock import MagicMock

from django.contrib.flatpages.models import FlatPage

from pytest import fixture, mark

from config.templatetags.custom_tags import jsonld, urljoin, vslice
from config.templatetags.flatpage_tags import breadcrumbs_ld


def test_url_join():
    assert urljoin('https://example.com', 'api/test') == \
        'https://example.com/api/test'
    assert urljoin('https://example.com/api', '/test') == \
        'https://example.com/test'
    assert urljoin('https://example.com', 'https://test.com') == \
        'https://test.com'


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
    pattern = r'<script.*?>(.*?)</script>'  # lgtm[py/bad-tag-filter]
    body = match(pattern, tag).group(1)
    assert '<' not in body
    assert '>' not in body
    assert '&' not in body


def test_vslice():
    value = [1, 2, 3, 4, 5, 6]
    assert vslice(value, 3) == [1, 2, 3]


@fixture
def mock_request(monkeypatch):
    fake_request = MagicMock()
    fake_request().build_absolute_uri.return_value = 'https://example.com'
    monkeypatch.setattr('django.http.request.HttpRequest', fake_request)


@mark.django_db
@mark.usefixtures('django_db_setup')
def test_breadcrumbs_ld(mock_request):
    from django.http.request import HttpRequest
    page = FlatPage.objects.first()
    assert 'About us' in breadcrumbs_ld(HttpRequest(), page)
