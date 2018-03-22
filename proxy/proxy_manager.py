import requests

from helpers.request import Request
from parsers.proxy_catalog_parser import ProxyCatalogParser


CHECK_PROXY_URL = 'https://ya.ru'


class ProxyManager(Request):
    def __init__(self, scrapper, timeout=10):
        super().__init__(timeout=timeout)
        self._scrapper = scrapper
        self._excluded_proxies = []

    def get_proxy(self):
        data = self._scrapper.scrape('proxy-list')
        parser = ProxyCatalogParser(data)
        for ip in parser.proxy_ips():
            url = 'http://{}'.format(ip)
            if url in self._excluded_proxies:
                continue
            try:
                self.proxy = url
                self.get()
                return url
            except (requests.ConnectionError, requests.ReadTimeout):
                continue
        return None

    def forget_proxy(self, url):
        self._excluded_proxies.append(url)

    def get_url(self):
        return CHECK_PROXY_URL
