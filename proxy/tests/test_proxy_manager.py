import os
import unittest
import re

import requests_mock

from proxy.proxy_manager import ProxyManager, CHECK_PROXY_URL


class MockScraper:
    def scrape(self, path, *, params=None, headers=None):
        path = re.sub(r'/', '-', path.lower().strip())
        base_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(base_path, 'responses/{}'.format(path)), 'r') as r:
            return r.read()


class TestProxyManager(unittest.TestCase):
    def setUp(self):
        self._manager = ProxyManager(MockScraper())

    def test_get_proxy(self):
        with requests_mock.mock() as m:
            m.get(CHECK_PROXY_URL, text='')
            proxy = self._manager.get_proxy()
            self.assertEqual('http://35.196.26.166:3128', proxy)

    def test_forget_proxy(self):
        with requests_mock.mock() as m:
            self._manager.forget_proxy('http://35.196.26.166:3128')
            m.get(CHECK_PROXY_URL, text='')
            proxy = self._manager.get_proxy()
            self.assertEqual('http://47.89.22.200:80', proxy)


if __name__ == '__main__':
    unittest.main()
