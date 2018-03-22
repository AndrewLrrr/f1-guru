import os
import unittest
from abc import ABC, abstractmethod

from parsers.proxy_catalog_parser import ProxyCatalogParser


class TestParser(ABC, unittest.TestCase):
    def setUp(self):
        base_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(base_path, self.get_response_file_path()), 'r') as r:
            self._parser = self.init_parser(r.read())

    @abstractmethod
    def init_parser(self, html):
        """Returns response handler"""

    @abstractmethod
    def get_response_file_path(self):
        """Returns path to response file"""


class TestProxyCalalogParser(TestParser):
    def test_proxy_ips(self):
        expected = ['186.94.46.203:8080', '54.169.9.27:8080', '94.23.56.95:8080', '180.251.56.84:3128',
                    '118.97.29.203:80', '66.70.191.5:3128', '5.196.189.50:8080', '167.205.6.6:80',
                    '85.235.188.194:8080', '198.50.219.232:8080', '194.14.207.87:80', '107.170.243.244:80',
                    '82.64.24.52:80', '52.40.59.11:80', '92.222.74.221:80', '37.187.116.199:80', '54.37.13.33:80',
                    '91.121.88.53:80', '111.13.109.27:80', '158.69.197.236:80', '74.208.110.38:80', '64.34.21.84:80',
                    '92.38.47.239:80', '173.212.202.65:80', '163.172.215.220:80', '52.57.95.123:80', '104.197.98.54:80',
                    '18.220.146.56:80', '51.15.160.216:80', '168.128.29.75:80', '95.85.50.218:80', '35.187.81.58:80',
                    '212.83.164.85:80', '176.31.50.61:80', '94.177.175.232:80', '52.163.62.13:80', '146.148.33.10:80',
                    '202.159.36.70:80', '35.202.22.18:80', '52.174.89.111:80', '115.70.186.106:8080',
                    '137.74.254.242:3128', '192.158.236.57:3128', '163.172.217.103:3128', '162.223.91.18:3128',
                    '165.227.53.107:3128', '54.36.182.96:3128', '195.154.163.181:3128', '89.236.17.106:3128',
                    '122.3.29.175:53281']

        actual = self._parser.proxy_ips()

        self.assertEqual(expected, actual)
        self.assertEqual(50, len(actual))

    def init_parser(self, html):
        return ProxyCatalogParser(html)

    def get_response_file_path(self):
        return 'responses/proxies_catalog_response.html'


if __name__ == '__main__':
    unittest.main()
