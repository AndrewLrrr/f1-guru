import re
import requests
from urllib.parse import urlencode, quote_plus
from abc import ABC, abstractmethod

from decorators.decorators import retry
from helpers.fields import CharField, DictionaryField, IntegerField, BooleanField


class Request(ABC):
    _url = CharField(required=True)
    _params = DictionaryField(nullable=True)
    _headers = DictionaryField(nullable=True)
    _secure = BooleanField()
    proxy = CharField(nullable=True)  # TODO: Возможно стоит сделать отлельное поле для url адреса
    timeout = IntegerField(required=True)

    def __init__(self, timeout=3, proxy=None):
        self.timeout = timeout
        self.proxy = proxy
        self._params = None
        self._headers = None

    def get(self, *, params=None, headers=None, secure=True):
        self._url = self.get_url()
        self._secure = secure
        if params is not None:
            self._params = params
        if headers is not None:
            self._headers = headers
        return self._do_get_request()

    def get_full_url(self):
        url = re.sub(r'/?$', '', self.get_url())
        if self._params is not None:
            return '{}?{}'.format(url, urlencode(self._params, quote_via=quote_plus))
        return url

    @abstractmethod
    def get_url(self):
        """Returns request url"""

    @retry(requests.RequestException)
    def _do_get_request(self):
        # TODO: Логировать все запросы в файл
        protocol = 'https' if self._secure else 'http'

        response = requests.get(
            url=self._url,
            timeout=self.timeout,
            params=self._params,
            headers=self._headers,
            proxies={protocol: self.proxy}
        )

        response.raise_for_status()

        return response.text
