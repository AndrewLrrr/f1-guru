import os
import unittest
from abc import ABC, abstractmethod

from parsers.f1_news_race_calatog_parser import F1NewsRaceCatalogParser
from parsers.f1_news_team_points_parser import F1NewsTeamPointsParser
from parsers.f1_news_testing_parser import F1NewsTestingParser
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


class TestF1NewsTestingParser(TestParser):
    def test_dates(self):
        self.assertEqual(['28 февраля', '27 февраля'], self._parser.dates())

    def test_results(self):
        results = self._parser.results()
        self.assertEqual(2, len(results))
        self.assertEqual(11, len(results[0]))
        self.assertEqual(11, len(results[1]))
        self.assertEqual('1', results[0][0][0])
        self.assertEqual('Райкконен', results[0][0][1])
        self.assertEqual('Ferrari', results[0][0][2])
        self.assertEqual('1.20.960', results[0][0][3])
        self.assertEqual('108', results[0][0][4])
        self.assertEqual('Soft', results[0][0][5])

        self.assertEqual('1', results[1][0][0])
        self.assertEqual('Хэмилтон', results[1][0][1])
        self.assertEqual('Mercedes', results[1][0][2])
        self.assertEqual('1.21.765', results[1][0][3])
        self.assertEqual('73', results[1][0][4])
        self.assertEqual('Soft', results[1][0][5])

        self.assertEqual('11', results[1][-1][0])
        self.assertEqual('Эриксон', results[1][-1][1])
        self.assertEqual('Sauber', results[1][-1][2])
        self.assertEqual('1.26.841', results[1][-1][3])
        self.assertEqual('72', results[1][-1][4])
        self.assertEqual('Medium', results[1][-1][5])

    def get_response_file_path(self):
        return 'responses/f1-news-testing-2017.html'

    def init_parser(self, html):
        return F1NewsTestingParser(html)


class TestF1NewsTeamPointsParser(TestParser):
    def test_points(self):
        result = self._parser.points()
        self.assertEqual(11, len(result))
        self.assertEqual(('1', 'Mercedes', '765'), result[0])
        self.assertEqual(('4', 'Force India', '173'), result[3])
        self.assertEqual(('6', 'McLaren', '76'), result[5])
        self.assertEqual(('11', 'Manor', '1'), result[10])

    def get_response_file_path(self):
        return 'responses/f1-news-team-points-2016.html'

    def init_parser(self, html):
        return F1NewsTeamPointsParser(html)


class TestF1NewsRaceCatalog(TestParser):
    def test_links(self):
        expected = (
            'https://f1news.ru/Championship/2016/australia/race.shtml',
            'https://f1news.ru/Championship/2016/bahrain/race.shtml',
            'https://f1news.ru/Championship/2016/china/race.shtml',
            'https://f1news.ru/Championship/2016/russia/race.shtml',
            'https://f1news.ru/Championship/2016/spain/race.shtml',
            'https://f1news.ru/Championship/2016/monaco/race.shtml',
            'https://f1news.ru/Championship/2016/canada/race.shtml',
            'https://f1news.ru/Championship/2016/europe/race.shtml',
            'https://f1news.ru/Championship/2016/austria/race.shtml',
            'https://f1news.ru/Championship/2016/britain/race.shtml',
            'https://f1news.ru/Championship/2016/hungary/race.shtml',
            'https://f1news.ru/Championship/2016/germany/race.shtml',
            'https://f1news.ru/Championship/2016/belgium/race.shtml',
            'https://f1news.ru/Championship/2016/italy/race.shtml',
            'https://f1news.ru/Championship/2016/singapore/race.shtml',
            'https://f1news.ru/Championship/2016/malaysia/race.shtml',
            'https://f1news.ru/Championship/2016/japan/race.shtml',
            'https://f1news.ru/Championship/2016/usa/race.shtml',
            'https://f1news.ru/Championship/2016/mexico/race.shtml',
            'https://f1news.ru/Championship/2016/brazil/race.shtml',
            'https://f1news.ru/Championship/2016/abudhabi/race.shtml',
        )
        self.assertEqual(expected, self._parser.links())

    def test_tracks(self):
        expected = (
            'Мельбурн',
            'Сахир',
            'Шанхай',
            'Сочи',
            'Барселона',
            'Монте-Карло',
            'Монреаль',
            'Баку',
            'Шпильберг',
            'Сильверстоун',
            'Будапешт',
            'Хоккенхайм',
            'Спа',
            'Монца',
            'Сингапур',
            'Сепанг',
            'Сузука',
            'Остин',
            'Мехико',
            'Сан-Паулу',
            'Яс-Марина',
        )
        self.assertEqual(expected, self._parser.tracks())

    def get_response_file_path(self):
        return 'responses/f1-news-race-catalog-2016.html'

    def init_parser(self, html):
        return F1NewsRaceCatalogParser(html)


if __name__ == '__main__':
    unittest.main()
