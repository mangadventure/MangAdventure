from django.core.cache.backends import memcached, redis

from pytest import importorskip, raises

from MangAdventure.cache import SignedPyLibMCCache, SignedRedisCache
from MangAdventure.tests.base import MangadvTestBase


class TestCache(MangadvTestBase):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        importorskip('redis', reason='requires redis')

    def setup_method(self):
        self.client = SignedRedisCache('', {})._class([''])
        self.og_client = redis.RedisCache('', {})._class([''])

    def test_int(self):
        data = self.client._serializer.dumps(3)
        assert isinstance(data, int)
        assert self.client._serializer.loads(data) == 3

    def test_pickle(self):
        data = self.client._serializer.dumps([])
        assert self.client._serializer.loads(data) == []

    def test_unsigned(self):
        from pickle import UnpicklingError
        with raises(UnpicklingError):
            data = self.og_client._serializer.dumps([])
            self.client._serializer.loads(data)


class TestMemcached(MangadvTestBase):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        importorskip('pylibmc', reason='requires pylimbc')

    def setup_method(self):
        self.client = SignedPyLibMCCache('', {})._class([''])
        self.og_client = memcached.PyLibMCCache('', {})._class([''])

    def test_str(self):
        data, flag = self.client.serialize('')
        assert flag & 23 == 16
        assert isinstance(data, bytes)
        assert self.client.deserialize(data, flag) == ''

    def test_pickle(self):
        data, flag = self.client.serialize([])
        assert flag & 23 == 1
        assert isinstance(data, bytes)
        assert self.client.deserialize(data, flag) == []

    def test_unsigned(self):
        from pickle import UnpicklingError
        with raises(UnpicklingError):
            data, flag = self.og_client.serialize([])
            self.client.deserialize(data, flag)
