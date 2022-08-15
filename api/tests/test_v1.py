from typing import Dict, List, Tuple, Union

from django.core.cache import cache
from django.http import JsonResponse
from django.urls import reverse

from pytest import mark

from groups.models import Group, Member, Role

from . import APITestBase


class APIViewTestBase(APITestBase):
    def get_data(self, url: str, params: Dict[str, str] = {}
                 ) -> Tuple[int, Union[Dict, List]]:
        """
        Helper function to get JSON data from an API URL
        in python data structures.

        :param url: The url to query for data.
        :param params: Optional URL params.

        :return: tuple of the response code and the JSON object
        """
        r = self.client.get(url, params)
        assert isinstance(r, JsonResponse)
        assert 'Warning' in r.headers
        return r.status_code, r.json()  # type: ignore

    def teardown_method(self):
        super().teardown_method()
        cache.clear()


class TestReleases(APIViewTestBase):
    URL = reverse('api:v1:releases')

    def test_get(self):
        status_code, data = self.get_data(self.URL)
        assert status_code == 200
        assert isinstance(data, List)
        assert len(data) == 1
        series1 = data[0]
        for field in ('slug', 'title', 'url', 'cover', 'latest_chapter'):
            assert field in series1
        for field in ('title', 'volume', 'number', 'date'):
            assert field in series1['latest_chapter']


class TestAllSeries(APIViewTestBase):
    URL = reverse('api:v1:all_series')

    def test_get(self):
        status_code, data = self.get_data(self.URL)
        assert status_code == 200
        assert isinstance(data, List)
        assert len(data) == 2
        series1 = data[0]
        fields = (
            'slug', 'title', 'aliases', 'url', 'description', 'authors',
            'artists', 'categories', 'cover', 'completed', 'volumes'
        )
        for field in fields:
            assert field in series1

    def test_get_slug(self):
        status_code, data = self.get_data(self.URL, {'slug': 'test-series'})
        assert status_code == 200
        assert isinstance(data, List)
        assert len(data) == 1

    def test_search(self):
        status_code, data = self.get_data(
            self.URL, {'categories': 'adventure'}
        )
        assert status_code == 200
        assert isinstance(data, List)
        assert len(data) == 1

    def test_post(self):
        r = self.client.post(self.URL)
        assert r.status_code == 405


class TestSeries(APIViewTestBase):
    URL = reverse('api:v1:series', kwargs={'slug': 'test-series'})

    def test_get(self):
        status_code, data = self.get_data(self.URL)
        assert status_code == 200
        assert isinstance(data, Dict)
        fields = (
            'slug', 'title', 'aliases', 'url', 'description', 'authors',
            'artists', 'categories', 'cover', 'completed', 'volumes'
        )
        for field in fields:
            assert field in data

    def test_not_found(self):
        status_code, data = self.get_data(
            reverse('api:v1:series', args=('no',))
        )
        assert status_code == 404
        assert 'error' in data
        assert data['error'] == 'Not found'


class TestVolume(APIViewTestBase):
    URL = reverse('api:v1:volume', kwargs={'slug': 'test-series', 'vol': 1})

    def test_get(self):
        status_code, data = self.get_data(self.URL)
        assert status_code == 200
        assert isinstance(data, Dict)
        assert '0' in data
        fields = (
            'title', 'url', 'pages_root',
            'pages_list', 'date', 'final', 'groups'
        )
        for field in fields:
            assert field in data['0']

    def test_not_found_series(self):
        url = reverse('api:v1:volume', kwargs={'slug': 'testseries', 'vol': 1})
        status_code, data = self.get_data(url)
        assert status_code == 404
        assert 'error' in data
        assert data['error'] == 'Not found'

    def test_not_found_volume(self):
        url = reverse('api:v1:volume', kwargs={'slug': 'test-series', 'vol': 0})
        status_code, data = self.get_data(url)
        assert status_code == 404
        assert 'error' in data
        assert data['error'] == 'Not found'


class TestChapter(APIViewTestBase):
    URL = reverse('api:v1:chapter', kwargs={
        'slug': 'test-series', 'vol': 1, 'num': 0.0
    })

    def test_get(self):
        status_code, data = self.get_data(self.URL)
        assert status_code == 200
        assert isinstance(data, Dict)
        fields = (
            'url', 'title', 'full_title', 'pages_root',
            'pages_list', 'date', 'final', 'groups'
        )
        for field in fields:
            assert field in data
        for field in ('id', 'name'):
            assert field in data['groups'][0]

    def test_not_found(self):
        url = reverse('api:v1:chapter', kwargs={
            'slug': 'test-series', 'vol': 1, 'num': 2.0
        })
        status_code, data = self.get_data(url)
        assert status_code == 404
        assert 'error' in data
        assert data['error'] == 'Not found'


class TestAllPeople(APIViewTestBase):
    @mark.parametrize('url', (
        reverse('api:v1:all_artists'), reverse('api:v1:all_authors')
    ))
    def test_get(self, url):
        status_code, data = self.get_data(url)
        assert status_code == 200
        assert isinstance(data, List)
        assert len(data) == 1
        person = data[0]
        for field in ('id', 'name', 'aliases', 'series'):
            assert field in person
        assert len(person['series']) == 1
        for field in ('slug', 'title', 'aliases'):
            assert field in person['series'][0]


class TestPerson(APIViewTestBase):
    @mark.parametrize('url', (
        reverse('api:v1:artist', kwargs={'p_id': 1}),
        reverse('api:v1:author', kwargs={'p_id': 1})
    ))
    def test_get(self, url):
        status_code, data = self.get_data(url)
        assert status_code == 200
        assert isinstance(data, Dict)
        for field in ('id', 'name', 'aliases', 'series'):
            assert field in data
        for field in ('slug', 'title', 'aliases'):
            assert field in data['series'][0]

    @mark.parametrize('url', (
        reverse('api:v1:artist', kwargs={'p_id': 4}),
        reverse('api:v1:author', kwargs={'p_id': 4})
    ))
    def test_not_found(self, url):
        status_code, data = self.get_data(url)
        assert status_code == 404
        assert 'error' in data
        assert data['error'] == 'Not found'


class TestAllGroups(APIViewTestBase):
    URL = reverse('api:v1:all_groups')

    def test_get_no_members(self):
        status_code, data = self.get_data(self.URL)
        assert status_code == 200
        assert isinstance(data, List)
        assert len(data) == 1
        group1 = data[0]
        fields = (
            'id', 'name', 'description', 'website',
            'discord', 'twitter', 'logo', 'members', 'series'
        )
        for field in fields:
            assert field in group1
        assert len(group1['series']) == 1
        assert len(group1['members']) == 0
        series1 = group1['series'][0]
        for field in ('slug', 'title', 'aliases'):
            assert field in series1

    def test_get_members(self):
        member = Member.objects.create(name='test')
        group = Group.objects.get(pk=1)
        Role.objects.create(member=member, group=group, role='LD')
        status_code, data = self.get_data(self.URL)
        assert status_code == 200
        group1 = data[0]
        assert len(group1['members']) == 1


class TestGroup(APIViewTestBase):
    URL = reverse('api:v1:group', kwargs={'g_id': 1})

    def test_get(self):
        status_code, data = self.get_data(self.URL)
        assert status_code == 200
        assert isinstance(data, Dict)
        fields = (
            'id', 'name', 'description', 'website',
            'discord', 'twitter', 'logo', 'members', 'series'
        )
        for field in fields:
            assert field in data

    def test_not_found(self):
        url = reverse('api:v1:group', kwargs={'g_id': 0})
        status_code, data = self.get_data(url)
        assert status_code == 404
        assert 'error' in data
        assert data['error'] == 'Not found'


class TestCategories(APIViewTestBase):
    URL = reverse('api:v1:categories')

    def test_get(self):
        status_code, data = self.get_data(self.URL)
        assert status_code == 200
        assert isinstance(data, List)
        category1 = data[0]
        for field in ('id', 'name', 'description'):
            assert field in category1
