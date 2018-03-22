import os
import shutil
import unittest

from decorators import decorators
from helpers.cacher import Cacher


FILE_SOURCE_NAME = 'http://test.com/some/url'

CACHE_PREFIX = 'test'


class TestMethodArgs:
    @decorators.save_to_cache_method(CACHE_PREFIX)
    def test(self, *args):
        return args[0]


class TestCacheDecorator(unittest.TestCase):
    def setUp(self):
        cacher = Cacher(CACHE_PREFIX)
        self.test_dir = cacher._directory_path

    def tearDown(self):
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_can_save_data_to_file(self):
        class Test:
            @decorators.save_to_cache_method(CACHE_PREFIX)
            def test(self, data):
                return data

        t = Test()
        res = t.test(FILE_SOURCE_NAME)
        self.assertEqual(res, FILE_SOURCE_NAME)
        self.assertEqual(1, len(os.listdir(self.test_dir)))

    def test_can_return_data_from_file(self):
        class Test:
            @decorators.save_to_cache_method(CACHE_PREFIX)
            def set_test_file(self, data):
                return data

            @decorators.save_to_cache_method(CACHE_PREFIX)
            def get_test_file(self, data):
                return 'Actual content must return decorator'

        t = Test()
        t.set_test_file(FILE_SOURCE_NAME)
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        res = t.get_test_file(FILE_SOURCE_NAME)
        self.assertEqual(res, FILE_SOURCE_NAME)

    def test_can_pack_and_unpack_static_methods(self):
        class Test:
            @staticmethod
            @decorators.save_to_cache_method(CACHE_PREFIX)
            def set_test_file(data):
                return data

            @staticmethod
            @decorators.save_to_cache_method(CACHE_PREFIX)
            def get_test_file(data):
                return 'Actual content must return decorator'

        t = Test()
        t.set_test_file(FILE_SOURCE_NAME)
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        res = t.get_test_file(FILE_SOURCE_NAME)
        self.assertEqual(res, FILE_SOURCE_NAME)

    def test_can_create_key_from_dict(self):
        t = TestMethodArgs()
        res = t.test({'test1': 1, 'test2': 2})
        self.assertEqual(res, {'test1': 1, 'test2': 2})
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        t2 = TestMethodArgs()
        res = t2.test({'test1': 1, 'test2': 2})
        self.assertEqual(res, {'test1': 1, 'test2': 2})
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        res = t2.test({'test1': 2, 'test2': 2})
        self.assertEqual(res, {'test1': 2, 'test2': 2})
        self.assertEqual(2, len(os.listdir(self.test_dir)))

    def test_can_create_key_from_list(self):
        t = TestMethodArgs()
        res = t.test([1, 2, 3])
        self.assertEqual(res, [1, 2, 3])
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        t2 = TestMethodArgs()
        res = t2.test([2, 1, 3])
        self.assertEqual(res, [1, 2, 3])
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        res = t.test([2, 2, 3])
        self.assertEqual(res, [2, 2, 3])
        self.assertEqual(2, len(os.listdir(self.test_dir)))

    def test_can_create_key_from_tuple(self):
        t = TestMethodArgs()
        res = t.test(tuple([1, 2, 3]))
        self.assertEqual(res, tuple([1, 2, 3]))
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        res = t.test(tuple([2, 3, 1]))
        self.assertEqual(res, tuple([2, 3, 1]))
        self.assertEqual(2, len(os.listdir(self.test_dir)))

        res = t.test(tuple([2, 3, 1]))
        self.assertEqual(res, tuple([2, 3, 1]))
        self.assertEqual(2, len(os.listdir(self.test_dir)))

        t2 = TestMethodArgs()
        res = t2.test(tuple([1, 2, 3]))
        self.assertEqual(res, tuple([1, 2, 3]))
        self.assertEqual(2, len(os.listdir(self.test_dir)))

        res = t2.test(tuple([2, 2, 3]))
        self.assertEqual(res, tuple([2, 2, 3]))
        self.assertEqual(3, len(os.listdir(self.test_dir)))

    def test_can_except_none_value(self):
        class Test:
            @decorators.save_to_cache_method(CACHE_PREFIX)
            def test(self, *args):
                return tuple(filter(None, args))

        t = Test()

        res = t.test(1, None)
        self.assertEqual(res, (1,))
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        res = t.test(1, 2, None)
        self.assertEqual(res, (1, 2,))
        self.assertEqual(2, len(os.listdir(self.test_dir)))

        res = t.test(1, 2, None)
        self.assertEqual(res, (1, 2,))
        self.assertEqual(2, len(os.listdir(self.test_dir)))

        res = t.test(1, None)
        self.assertEqual(res, (1,))
        self.assertEqual(2, len(os.listdir(self.test_dir)))

    def test_can_disable_decorator(self):
        tmp = decorators.save_to_cache_method
        decorators.save_to_cache_method = decorators.disable_cache

        class Test:
            @decorators.save_to_cache_method(CACHE_PREFIX)
            def set_test_file(self, data):
                return data

            @decorators.save_to_cache_method(CACHE_PREFIX)
            def get_test_file(self, data):
                return 'Actual content must NOT return decorator'

        t = Test()
        t.set_test_file(FILE_SOURCE_NAME)
        self.assertFalse(os.path.isdir(self.test_dir))

        res = t.get_test_file(FILE_SOURCE_NAME)
        self.assertEqual(res, 'Actual content must NOT return decorator')

        decorators.save_to_cache_method = tmp  # back to origin decorator


if __name__ == '__main__':
    unittest.main()
