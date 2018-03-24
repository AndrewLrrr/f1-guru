import unittest

from helpers.helpers import add_milliseconds_to_time


class TestHelpers(unittest.TestCase):
    def test_add_milliseconds_to_time(self):
        self.assertEqual('1.21.623', add_milliseconds_to_time('1.21.123', 500))
        self.assertEqual('1.22.123', add_milliseconds_to_time('1.21.623', 500))
        self.assertEqual('1.23.323', add_milliseconds_to_time('1.22.123', 1200))


if __name__ == '__main__':
    unittest.main()
