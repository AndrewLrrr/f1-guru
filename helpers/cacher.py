import os
import pickle
import errno
import re
import shutil

from settings import STORAGE_PATH


class Cacher:
    _protocol = 2

    def __init__(self, prefix=''):
        prefix = re.sub('([\w-]+)', '\1', prefix)
        if not prefix:
            raise ValueError('Incorrect cache key')
        self._directory_path = os.path.join(STORAGE_PATH, 'cache', prefix)

    def put(self, key, value):
        try:
            os.makedirs(self._directory_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        file_path = os.path.join(self._directory_path, key)
        if os.path.isfile(file_path):
            return False
        with open(file_path, mode='wb') as fn:
            pickle.dump(value, fn, self._protocol)
        return True

    def get(self, key):
        file_path = os.path.join(self._directory_path, key)
        if os.path.isfile(file_path):
            with open(file_path, mode='rb') as fn:
                res = pickle.load(fn)
            return res
        else:
            return None

    def has(self, key):
        file_path = os.path.join(self._directory_path, key)
        return os.path.isfile(file_path)

    def update(self, key, value):
        file_path = os.path.join(self._directory_path, key)
        if os.path.isfile(file_path):
            with open(file_path, mode='wb') as fn:
                pickle.dump(value, fn, self._protocol)
            return True
        return False

    def delete(self, key):
        file_path = os.path.join(self._directory_path, key)
        try:
            os.remove(file_path)
            return True
        except OSError:
            return False

    def flush(self):
        try:
            shutil.rmtree(self._directory_path)
            return True
        except OSError:
            return False
