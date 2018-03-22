import unittest

from decorators import decorators


class TestRetryDecorator(unittest.TestCase):
    def setUp(self):
        self._counter = 0

    def test_retry_on_exception_raised(self):
        @decorators.retry(RuntimeError, tries=3, delay=0.1, backoff=1)
        def test():
            self._counter += 1
            if self._counter < 3:
                raise RuntimeError
            return self._counter

        _counter = test()

        self.assertEqual(3, _counter)


if __name__ == '__main__':
    unittest.main()
