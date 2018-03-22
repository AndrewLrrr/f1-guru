import unittest

import requests
import requests_mock

from exceptions.exceptions import ProxyScraperException
from helpers.scraper import Scraper, ProxyScraper


class TestScraper(unittest.TestCase):
    def test_can_correctly_do_simple_scrape(self):
        s = Scraper(host='test.com', protocol='http', port=8080)

        with requests_mock.mock() as m:
            try:
                s.scrape(path='path')
            except requests_mock.exceptions.NoMockAddress:
                pass
            m.get(s.get_full_url(), text='test content')
            self.assertEqual('test content', s.scrape(path='path'))
            self.assertEqual('http://test.com:8080/path', s.get_full_url())

    def test_can_correctly_do_scrape_with_params(self):
        s = Scraper(host='test.com', protocol='http', port=8080)
        params = {'q': 'query', 'page': 1}

        with requests_mock.mock() as m:
            try:
                s.scrape(path='path', params=params)
            except requests_mock.exceptions.NoMockAddress:
                pass
            m.get(s.get_full_url(), text='test content')
            self.assertEqual('test content', s.scrape(path='path', params=params))
            self.assertRegex(s.get_full_url(), r'http://test.com:8080/path\?(?:q=query&page=1|page=1&q=query)')

    def test_can_correctly_do_scrape_with_incorrect_host(self):
        s = Scraper(host='http://test.com', protocol='https')
        params = {'q': 'query', 'page': 1}

        with requests_mock.mock() as m:
            try:
                s.scrape(path='path', params=params)
            except requests_mock.exceptions.NoMockAddress:
                pass
            m.get(s.get_full_url(), text='test content')
            self.assertEqual('test content', s.scrape(path='path', params=params))
            self.assertRegex(s.get_full_url(), r'https://test.com/path\?(?:q=query&page=1|page=1&q=query)')

    def test_can_correctly_do_scrape_with_extra_slashes(self):
        s = Scraper(host='http://test.com/', protocol='https')
        params = {'q': 'query', 'page': 1}

        with requests_mock.mock() as m:
            try:
                s.scrape(path='/path/', params=params)
            except requests_mock.exceptions.NoMockAddress:
                pass
            m.get(s.get_full_url(), text='test content')
            self.assertEqual('test content', s.scrape(path='/path/', params=params))
            self.assertRegex(s.get_full_url(), r'https://test.com/path\?(?:q=query&page=1|page=1&q=query)')

    def test_raise_exception_if_incorrect_protocol(self):
        with self.assertRaises(ValueError) as context:
            Scraper(host='http://test.com', protocol='ftp')
        self.assertEqual('Unsupported protocol `ftp`. You must use `http` or `https` only', str(context.exception))


class MockProxyManager:
    def __init__(self):
        self._excluded_proxies = []
        self._proxies = ('185.82.212.95:8080', '190.7.112.18:3128', '195.128.115.30:53281')

    def get_proxy(self):
        for ip in self._proxies:
            url = 'http://{}'.format(ip)
            if url in self._excluded_proxies:
                continue
            return url
        return None

    def forget_proxy(self, url):
        self._excluded_proxies.append(url)


class MockScraper:
    def __init__(self):
        self.proxy = None
        self.counter = 0

    def scrape(self, path, *, params=None, headers=None):
        if self.proxy == 'http://185.82.212.95:8080' and self.counter == 0:
            return 'test1'
        elif self.proxy == 'http://185.82.212.95:8080' and self.counter == 1:
            raise requests.ConnectionError
        elif self.proxy == 'http://190.7.112.18:3128' and self.counter == 1:
            return 'test2'
        elif self.proxy == 'http://190.7.112.18:3128' and self.counter == 2:
            raise requests.ReadTimeout
        elif self.proxy == 'http://195.128.115.30:53281' and self.counter == 2:
            return 'test3'
        elif self.proxy == 'http://195.128.115.30:53281' and self.counter == 3:
            return 'test4'
        else:
            raise requests.ConnectionError


class TestProxyScraper(unittest.TestCase):
    def setUp(self):
        self._scraper = ProxyScraper('test.com', retries=2)
        self._scraper._proxy_manager = MockProxyManager()
        self._scraper._scraper = MockScraper()

    def test_scrape_and_reconnect(self):
        self.assertEqual('test1', self._scraper.scrape())
        self.assertEqual('http://185.82.212.95:8080', self._scraper._proxy)
        self._scraper._scraper.counter += 1
        self.assertEqual('test2', self._scraper.scrape())
        self.assertEqual('http://190.7.112.18:3128', self._scraper._proxy)
        self._scraper._scraper.counter += 1
        self.assertEqual('test3', self._scraper.scrape())
        self.assertEqual('http://195.128.115.30:53281', self._scraper._proxy)
        self._scraper._scraper.counter += 1
        self.assertEqual('test4', self._scraper.scrape())
        self.assertEqual('http://195.128.115.30:53281', self._scraper._proxy)
        self._scraper._scraper.counter += 1

        with self.assertRaises(ProxyScraperException) as context:
            self.assertIsNone(self._scraper.scrape())
        self.assertEqual('Ended attempts to proxy reconnect. Reason ``', str(context.exception))


if __name__ == '__main__':
    unittest.main()
