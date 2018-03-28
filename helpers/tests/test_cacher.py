import os
import shutil
import unittest

from helpers import cacher


class TestCacher(unittest.TestCase):
    cache_prefix = 'test'

    def setUp(self):
        self.c = cacher.Cacher(self.cache_prefix)
        self.test_dir = self.c._directory_path

    def tearDown(self):
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_put(self):
        self.c._directory_path = self.test_dir
        res = self.c.put('f', 'test')
        self.assertTrue(res)
        self.assertEqual(1, len(os.listdir(self.test_dir)))

    def test_get(self):
        self.c._directory_path = self.test_dir
        self.c.put('f', 'test')

        c2 = cacher.Cacher(self.cache_prefix)
        c2._directory_path = self.test_dir
        val = c2.get('f')
        self.assertEqual('test', val)

    def test_has(self):
        self.c._directory_path = self.test_dir
        self.c.put('f', 'test')

        c2 = cacher.Cacher(self.cache_prefix)
        c2._directory_path = self.test_dir
        self.assertTrue(c2.has('f'))
        self.assertFalse(c2.has('f2'))

    def test_delete(self):
        self.c._directory_path = self.test_dir
        self.c.put('f', 'test')
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        c2 = cacher.Cacher(self.cache_prefix)
        c2._directory_path = self.test_dir
        c2.delete('f')
        self.assertEqual(0, len(os.listdir(self.test_dir)))

    def test_flush(self):
        self.c._directory_path = self.test_dir
        self.c.put('f', 'test')
        self.c.put('f2', 'test2')
        self.assertEqual(2, len(os.listdir(self.test_dir)))
        self.assertTrue(os.path.isdir(self.test_dir))

        self.c.flush()
        self.assertFalse(os.path.isdir(self.test_dir))

    def test_cache_dict(self):
        self.c._directory_path = self.test_dir
        self.c.put('f', {'test1': 1, 'test2': 2})

        c2 = cacher.Cacher(self.cache_prefix)
        c2._directory_path = self.test_dir
        val = c2.get('f')
        self.assertEqual({'test1': 1, 'test2': 2}, val)

    def test_cache_list(self):
        self.c._directory_path = self.test_dir
        self.c.put('f', [1, 2, 3])

        c2 = cacher.Cacher(self.cache_prefix)
        c2._directory_path = self.test_dir
        val = c2.get('f')
        self.assertEqual([1, 2, 3], val)

    def test_cache_tuple(self):
        self.c._directory_path = self.test_dir
        self.c.put('f', tuple([1, 2, 3]))

        c2 = cacher.Cacher(self.cache_prefix)
        c2._directory_path = self.test_dir
        val = c2.get('f')
        self.assertEqual(tuple([1, 2, 3]), val)

    def test_cache_set(self):
        self.c._directory_path = self.test_dir
        self.c.put('f', {1, 2, 3})

        c2 = cacher.Cacher(self.cache_prefix)
        c2._directory_path = self.test_dir
        val = c2.get('f')
        self.assertEqual({1, 2, 3}, val)

    def test_cache_int(self):
        self.c._directory_path = self.test_dir
        self.c.put('f', 1)

        c2 = cacher.Cacher(self.cache_prefix)
        c2._directory_path = self.test_dir
        val = c2.get('f')
        self.assertEqual(1, val)

    def test_cache_float(self):
        self.c._directory_path = self.test_dir
        self.c.put('f', 1.5)

        c2 = cacher.Cacher(self.cache_prefix)
        c2._directory_path = self.test_dir
        val = c2.get('f')
        self.assertEqual(1.5, val)

    def test_incorrect_prefix_exception(self):
        with self.assertRaises(ValueError) as context:
            cacher.Cacher('/root')
        self.assertEqual('Incorrect cache prefix', str(context.exception))
        with self.assertRaises(ValueError) as context:
            cacher.Cacher('..root')
        self.assertEqual('Incorrect cache prefix', str(context.exception))
        with self.assertRaises(ValueError) as context:
            cacher.Cacher('root/')
        self.assertEqual('Incorrect cache prefix', str(context.exception))
        with self.assertRaises(ValueError) as context:
            cacher.Cacher('../root')
        self.assertEqual('Incorrect cache prefix', str(context.exception))


if __name__ == '__main__':
    unittest.main()
