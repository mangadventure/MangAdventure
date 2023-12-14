from hashlib import blake2b
from pickle import UnpicklingError, dumps, loads
from secrets import compare_digest
from typing import Any

from django.conf import settings
from django.core.cache.backends.memcached import PyLibMCCache
from django.core.cache.backends.redis import (
    RedisCache, RedisCacheClient, RedisSerializer
)


def _sign_data(data: bytes) -> bytes:
    return blake2b(
        data, digest_size=16,
        key=settings.SECRET_KEY.encode()
    ).digest()


class SignedRedisCache(RedisCache):
    "A cache binding using redis and signed pickles"

    def __init__(self, *args):
        super().__init__(*args)

        class _SignedRedisSerializer(RedisSerializer):
            def dumps(self, obj: Any) -> Any:
                if type(obj) is int:
                    return obj
                data = dumps(obj, self.protocol)
                return _sign_data(data) + data

            def loads(self, data: Any) -> Any:
                try:
                    return int(data)
                except ValueError:
                    sig, obj = data[:16], data[16:]
                    if compare_digest(sig, _sign_data(obj)):
                        return loads(obj)
                    raise UnpicklingError('Signatures do not match')

        class _SignedRedisCacheClient(RedisCacheClient):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._serializer = _SignedRedisSerializer()

        self._class = _SignedRedisCacheClient


class SignedPyLibMCCache(PyLibMCCache):
    "A cache binding using pylibmc and signed pickles"

    def __init__(self, *args):
        super().__init__(*args)

        def _is_pickle(flag: int) -> bool:
            return flag & 23 == 1

        class _SignedMCClient(self._lib.Client):
            def serialize(self, value: Any) -> tuple[bytes, int]:
                data, flag = super().serialize(value)
                if _is_pickle(flag):
                    return _sign_data(data) + data, flag
                return data, flag

            def deserialize(self, data: bytes, flag: int) -> Any:
                if _is_pickle(flag):
                    sig, obj = data[:16], data[16:]
                    if compare_digest(sig, _sign_data(obj)):
                        return loads(obj)
                    raise UnpicklingError('Signatures do not match')
                return super().deserialize(data, flag)

        self._class = _SignedMCClient


__all__ = ['SignedRedisCache', 'SignedPyLibMCCache']
