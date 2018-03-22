import os
import shutil
import unittest

from decorators import decorators
from helpers.cacher import Cacher

FILE_SOURCE_NAME = 'http://test.com/some/url'


class TestCacheDecorator(unittest.TestCase):
    def setUp(self):
        self.cache_prefix = 'test'
        cacher = Cacher(self.cache_prefix)
        self.test_dir = cacher._directory_path

    def tearDown(self):
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_can_save_data_to_file(self):
        @decorators.save_to_cache(self.cache_prefix)
        def test(data):
            return data

        res = test(FILE_SOURCE_NAME)
        self.assertEqual(res, FILE_SOURCE_NAME)
        self.assertEqual(1, len(os.listdir(self.test_dir)))

    def test_can_return_data_from_file(self):
        @decorators.save_to_cache(self.cache_prefix)
        def set_test_file(data):
            return data

        set_test_file(FILE_SOURCE_NAME)
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        @decorators.save_to_cache(self.cache_prefix)
        def get_test_file(data):
            return 'Actual content must return decorator'

        res = get_test_file(FILE_SOURCE_NAME)
        self.assertEqual(res, FILE_SOURCE_NAME)

    def test_can_create_key_from_dict(self):
        @decorators.save_to_cache(self.cache_prefix)
        def test(*args):
            return args[0]

        res = test({'test1': 1, 'test2': 2})
        self.assertEqual(res, {'test1': 1, 'test2': 2})
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        res = test({'test1': 1, 'test2': 2})
        self.assertEqual(res, {'test1': 1, 'test2': 2})
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        res = test({'test1': 2, 'test2': 2})
        self.assertEqual(res, {'test1': 2, 'test2': 2})
        self.assertEqual(2, len(os.listdir(self.test_dir)))

    def test_can_create_key_from_list(self):
        @decorators.save_to_cache(self.cache_prefix)
        def test(*args):
            return args[0]

        res = test([1, 2, 3])
        self.assertEqual(res, [1, 2, 3])
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        res = test([2, 1, 3])
        self.assertEqual(res, [1, 2, 3])
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        res = test([2, 2, 3])
        self.assertEqual(res, [2, 2, 3])
        self.assertEqual(2, len(os.listdir(self.test_dir)))

    def test_can_create_key_from_tuple(self):
        @decorators.save_to_cache(self.cache_prefix)
        def test(*args):
            return args[0]

        res = test(tuple([1, 2, 3]))
        self.assertEqual(res, tuple([1, 2, 3]))
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        res = test(tuple([2, 3, 1]))
        self.assertEqual(res, tuple([2, 3, 1]))
        self.assertEqual(2, len(os.listdir(self.test_dir)))

        res = test(tuple([2, 3, 1]))
        self.assertEqual(res, tuple([2, 3, 1]))
        self.assertEqual(2, len(os.listdir(self.test_dir)))

        res = test(tuple([1, 2, 3]))
        self.assertEqual(res, tuple([1, 2, 3]))
        self.assertEqual(2, len(os.listdir(self.test_dir)))

        res = test(tuple([2, 2, 3]))
        self.assertEqual(res, tuple([2, 2, 3]))
        self.assertEqual(3, len(os.listdir(self.test_dir)))

    def test_can_except_none_value(self):
        @decorators.save_to_cache(self.cache_prefix)
        def test(*args):
            return tuple(filter(None, args))

        res = test(1, None)
        self.assertEqual(res, (1,))
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        res = test(1, 2, None)
        self.assertEqual(res, (1, 2,))
        self.assertEqual(2, len(os.listdir(self.test_dir)))

        res = test(1, 2, None)
        self.assertEqual(res, (1, 2,))
        self.assertEqual(2, len(os.listdir(self.test_dir)))

        res = test(1, None)
        self.assertEqual(res, (1,))
        self.assertEqual(2, len(os.listdir(self.test_dir)))

    def test_can_disable_decorator(self):
        tmp = decorators.save_to_cache
        decorators.save_to_cache = decorators.disable_cache

        @decorators.save_to_cache(self.cache_prefix)
        def set_test_file(data):
            return data

        set_test_file(FILE_SOURCE_NAME)
        self.assertFalse(os.path.isdir(self.test_dir))

        @decorators.save_to_cache(self.cache_prefix)
        def get_test_file(data):
            return 'Actual content must NOT return decorator'

        res = get_test_file(FILE_SOURCE_NAME)
        self.assertEqual(res, 'Actual content must NOT return decorator')

        decorators.save_to_cache = tmp  # back to origin decorator


if __name__ == '__main__':
    unittest.main()
