import re

import requests

import settings
from exceptions.exceptions import ProxyScraperException
from helpers.fields import CharField, IntegerField
from helpers.request import Request
from proxy.proxy_manager import ProxyManager


class Scraper(Request):
    _path = CharField(required=False)
    _port = IntegerField(nullable=True)
    _protocol = CharField(required=True)

    def __init__(self, host, *, protocol='http', port=None, proxy=None, timeout=3):
        super().__init__(timeout, proxy)
        self._host = host.lower().strip()
        self._protocol = protocol.lower()
        self._port = port
        self.proxy = proxy
        if self._protocol not in ('http', 'https',):
            raise ValueError('Unsupported protocol `{}`. You must use `http` or `https` only'.format(protocol))

    def scrape(self, uri, *, params=None, headers=None):
        self._path = re.sub(r'^/?(.*?)/?$', r'\1', uri.lower().strip())
        secure = self._protocol == 'https'
        return self.get(params=params, headers=headers, secure=secure)

    def get_url(self):
        if self._host.startswith('http'):
            self._host = re.sub(r'^http[s]?://(.*?)/?$', r'\1', self._host)
        url = '{}://{}{}'.format(self._protocol, self._host, ':{}'.format(self._port) if self._port is not None else '')
        return '{}/{}'.format(url, re.sub(r'^/', '', self._path))


class ProxyScraper:
    def __init__(self, host, *, protocol='http', port=None, timeout=10, retries=10):
        proxy_scraper = Scraper(settings.PROXY_CATALOG_DOMAIN, protocol=settings.PROXY_CATALOG_PROTOCOL)
        self._proxy_manager = ProxyManager(proxy_scraper)
        self._proxy = None
        self._retries = retries
        self._scraper = Scraper(host, protocol=protocol, port=port, timeout=timeout)

    def scrape(self, uri='', *, params=None, headers=None):
        if self._proxy is None:
            self._proxy = self._proxy_manager.get_proxy()
            if not self._proxy:
                raise ProxyScraperException('Proxy not found')
            self._scraper.proxy = self._proxy
        try:
            return self._scraper.scrape(uri, params=params, headers=headers)
        except (requests.ConnectionError, requests.ReadTimeout) as e:
            if self._retries == 0:
                raise ProxyScraperException('Ended attempts to proxy reconnect. Reason `{}`'.format(e))
            self._proxy_manager.forget_proxy(self._proxy)
            self._retries -= 1
            self._proxy = None
            return self.scrape(uri, params=params, headers=headers)
        except Exception as e:
            ProxyScraperException(e)
