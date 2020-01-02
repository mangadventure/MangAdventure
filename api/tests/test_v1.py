from typing import Dict, List, Tuple, Union

from django.core.cache import cache
from django.http import JsonResponse
from django.urls import reverse

from pytest import mark

from api.response import JsonError
from groups.models import Group, Member, Role

from . import APITestBase


class APIViewTestBase(APITestBase):
    def get_data(self, url: str) -> Tuple[int, Union[Dict, List]]:
        """
        Helper function to get JSON data from an API URL
        in python data structures.

        :param url: The url to query for data.

        :return: tuple of the response code and the JSON object
        """
        r = self.client.get(url)
        assert type(r) in [JsonResponse, JsonError]
        return r.status_code, r.json()

    def teardown_method(self):
        super().teardown_method()
        cache.clear()


class TestReleases(APIViewTestBase):
    URL = reverse('api:v1:releases')

    def test_get(self):
        status_code, data = self.get_data(self.URL)
        assert status_code == 200
        assert type(data) == list
        assert len(data) == 2
        series1 = data[0]
        for field in ["slug", "title", "url", "cover", "latest_chapter"]:
            assert field in series1

        for field in ["title", "volume", "number", "date"]:
            assert field in series1["latest_chapter"]
        series2 = data[1]
        assert series2["latest_chapter"] == {}


class TestAllSeries(APIViewTestBase):
    URL = reverse('api:v1:all_series')

    def test_get(self):
        status_code, data = self.get_data(self.URL)
        assert status_code == 200
        assert type(data) == list
        assert len(data) == 2
        series1 = data[0]
        for field in ["slug", "title", "aliases", "url", "description",
                      "authors", "artists", "categories", "cover",
                      "completed", "volumes"]:
            assert field in series1


class TestSeries(APIViewTestBase):
    URL = reverse('api:v1:series', kwargs={'slug': 'test-series'})

    def test_get(self):
        status_code, data = self.get_data(self.URL)
        assert status_code == 200
        assert type(data) == dict
        for field in ["slug", "title", "aliases", "url", "description",
                      "authors", "artists", "categories", "cover",
                      "completed", "volumes"]:
            assert field in data

    def test_not_found(self):
        status_code, data = self.get_data(reverse('api:v1:series', args=['no']))
        assert status_code == 404
        assert 'error' in data
        assert data['error'] == 'Not found'


class TestVolume(APIViewTestBase):
    URL = reverse('api:v1:volume', kwargs={'slug': 'test-series', 'vol': 1})

    def test_get(self):
        status_code, data = self.get_data(self.URL)
        assert status_code == 200
        assert type(data) == dict
        assert "0" in data
        for field in ['title', 'url', 'pages_root', 'pages_list', 'date',
                      'final', 'groups']:
            assert field in data["0"]

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
    URL = reverse('api:v1:chapter', kwargs={'slug': 'test-series', 'vol': 1,
                                            'num': '0.0'})

    def test_get(self):
        status_code, data = self.get_data(self.URL)
        assert status_code == 200
        assert type(data) == dict
        for field in ['title', 'url', 'pages_root', 'pages_list', 'date',
                      'final', 'groups']:
            assert field in data
        for field in ['id', 'name']:
            assert field in data['groups'][0]

    def test_not_found(self):
        url = reverse('api:v1:chapter', kwargs={'slug': 'test-series', 'vol': 1,
                                                'num': '2.0'})
        status_code, data = self.get_data(url)
        print(data)
        assert status_code == 404
        assert 'error' in data
        assert data['error'] == 'Not found'


class TestAllPeople(APIViewTestBase):
    @mark.parametrize('url', [reverse('api:v1:all_artists'),
                              reverse('api:v1:all_authors')])
    def test_get(self, url):
        status_code, data = self.get_data(url)
        assert status_code == 200
        assert type(data) == list
        assert len(data) == 1
        person = data[0]
        for field in ['id', 'name', 'aliases', 'series']:
            assert field in person
        assert len(person['series']) == 1
        for field in ['slug', 'title', 'aliases']:
            assert field in person['series'][0]


class TestPerson(APIViewTestBase):
    @mark.parametrize('url', [reverse('api:v1:artist', kwargs={'p_id': 1}),
                              reverse('api:v1:author', kwargs={'p_id': 1})])
    def test_get(self, url):
        status_code, data = self.get_data(url)
        assert status_code == 200
        assert type(data) == dict
        for field in ['id', 'name', 'aliases', 'series']:
            assert field in data
        for field in ['slug', 'title', 'aliases']:
            assert field in data['series'][0]

    @mark.parametrize('url', [reverse('api:v1:artist', kwargs={'p_id': 4}),
                              reverse('api:v1:author', kwargs={'p_id': 4})])
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
        assert type(data) == list
        assert len(data) == 1
        group1 = data[0]
        for field in ['id', 'name', 'description', 'website', 'discord',
                      'twitter', 'logo', 'members', 'series']:
            assert field in group1
        assert len(group1['series']) == 1
        assert len(group1['members']) == 0
        series1 = group1['series'][0]
        for field in ['slug', 'title', 'aliases']:
            assert field in series1

    def test_get_members(self):
        member = Member.objects.create(name="test")
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
        assert type(data) == dict
        for field in ['id', 'name', 'description', 'website', 'discord',
                      'twitter', 'logo', 'members', 'series']:
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
        assert type(data) == list
        category1 = data[0]
        for field in ['id', 'name', 'description']:
            assert field in category1


class TestInvalid(APIViewTestBase):
    URL = reverse('api:v1:root')

    def test_get(self):
        status_code, _ = self.get_data(self.URL)
        assert status_code == 501

    def test_post(self):
        url = reverse('api:v1:all_series')
        r = self.client.post(url)
        assert r.status_code == 405
