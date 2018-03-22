import unittest
import requests_mock

from helpers.request import Request


class FakeRequest(Request):
    def __init__(self, proxy=None):
        super().__init__(proxy=proxy)
        self._params = {'test': 1}

    def get_url(self):
        return 'http://test1.com'


class FakeRequestWithEmptyUrl(Request):
    def get_url(self):
        return ''


class TestRequest(unittest.TestCase):
    def test_can_correctly_do_request(self):
        fr = FakeRequest()

        with requests_mock.mock() as m:
            m.get(fr.get_full_url(), text='test1')
            self.assertEqual('test1', fr.get())

    def test_can_correctly_do_request_with_custom_header(self):
        fr = FakeRequest()
        headers = {
            'User-Agent': 'Hello my name is test bot and I need some data from you:)'
        }

        with requests_mock.mock() as m:
            m.get(fr.get_full_url(), text='test1')
            self.assertEqual('test1', fr.get(headers=headers))
            self.assertEqual('Hello my name is test bot and I need some data from you:)', fr._headers['User-Agent'])

    def test_can_correctly_do_request_with_custom_proxy(self):
        proxy = 'http://127.0.0.1/'
        fr = FakeRequest(proxy=proxy)
        headers = {
            'User-Agent': 'Hello my name is test bot and I need some data from you:)'
        }

        with requests_mock.mock() as m:
            m.get(fr.get_full_url(), text='test1')
            self.assertEqual('test1', fr.get(headers=headers))
            self.assertEqual('Hello my name is test bot and I need some data from you:)', fr._headers['User-Agent'])
            self.assertEqual('http://127.0.0.1/', fr.proxy)

    def test_raise_value_error_if_url_is_empty(self):
        fr = FakeRequestWithEmptyUrl()

        with self.assertRaises(ValueError) as context:
            fr.get()
        self.assertTrue('CharField cannot be empty or blank', context.exception)

    def test_raise_value_error_if_timeout_is_empty(self):
        fr = FakeRequest()

        with self.assertRaises(ValueError) as context:
            fr.timeout = 0
            fr.get()
        self.assertTrue('IntegerField cannot be empty or blank', context.exception)


if __name__ == '__main__':
    unittest.main()
