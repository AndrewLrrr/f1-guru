import functools
import hashlib
import collections
from abc import ABC, abstractmethod
import time

from helpers.cacher import Cacher

BUILD_IN_TYPES = (str, int, float, complex, tuple, list, dict, set)


def retry(ExceptionToCheck, tries=3, delay=0.5, backoff=2):
    def deco_retry(f):
        @functools.wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck:
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry

    return deco_retry


class SaveToCache(ABC):
    def __init__(self, prefix=''):
        self._cacher = Cacher(prefix)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args):
            if not isinstance(args, collections.Hashable):
                return func(*args)
            cache_key = self._generate_cache_key(*args)
            value = self._cacher.get(cache_key)
            if value is None:
                value = func(*args)
                if value is not None:
                    self._cacher.put(cache_key, value)
            return value
        return wrapper

    def _generate_cache_key(self, *args):
        local_args = self._get_args(*args)
        hashes = []
        for arg in local_args:
            if arg is None:
                continue
            if not isinstance(arg, BUILD_IN_TYPES):
                return
            if isinstance(arg, dict):
                hashes.append(str(sorted(arg.items(), key=lambda x: x[0])))
            elif isinstance(arg, list):
                arg.sort()
                hashes.append(str(arg))
            elif isinstance(arg, str):
                hashes.append(arg)
            else:
                hashes.append(str(arg))
        return hashlib.md5(''.join(hashes).encode('utf-8')).hexdigest()

    @abstractmethod
    def _get_args(self, *args):
        """Возращает аргументы из которых будет создано имя для кеширования
        :param tuple args:
        """


class CacheFunction(SaveToCache):
    def _get_args(self, *args):
        return list(args)


class CacheMethod(SaveToCache):
    def _get_args(self, *args):
        _obj = args[0]
        if not isinstance(_obj, BUILD_IN_TYPES):
            return list(args)[1:]
        return list(args)  # if @staticmethod


class DisableCache:
    def __init__(self, prefix=''):
        self._prefix = prefix

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args):
            return func(*args)
        return wrapper


def disable_cache(prefix):
    return DisableCache(prefix)


def save_to_cache(prefix):
    return CacheFunction(prefix)


def save_to_cache_method(prefix):
    return CacheMethod(prefix)
