import os
import unittest
from abc import ABC, abstractmethod

from parsers.f1_news_race_calatog_parser import F1NewsRaceCatalogParser
from parsers.f1_news_race_result_parser import F1NewsRaceResultParser
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

    def test_track(self):
        self.assertEqual('Барселона', self._parser.track())

    def test_results(self):
        expected = [
            [
                ['1', 'Райкконен', 'Ferrari', '1.20.960', '108', 'Soft'],
                ['2', 'Хэмилтон', 'Mercedes', '1.20.983', '66', 'SuperSoft'],
                ['3', 'Ферстаппен', 'Red Bull Racing', '1.22.200', '89', 'Soft'],
                ['4', 'Магнуссен', 'Haas', '1.22.204', '118', 'SuperSoft'],
                ['5', 'Окон', 'Force India', '1.22.509', '86', 'SuperSoft'],
                ['6', 'Квят', 'Toro Rosso', '1.22.956', '68', 'Soft'],
                ['7', 'Боттас', 'Mercedes', '1.22.986', '102', 'Soft'],
                ['8', 'Палмер', 'Renault', '1.24.139', '53', 'Soft'],
                ['9', 'Джовинацци', 'Sauber', '1.24.617', '67', 'Soft'],
                ['10', 'Вандорн', 'McLaren', '1.25.600', '40', 'Soft'],
                ['11', 'Стролл', 'Williams', '1.26.040', '12', 'Medium']],
            [
                ['1', 'Хэмилтон', 'Mercedes', '1.21.765', '73', 'Soft'],
                ['2', 'Феттель', 'Ferrari', '1.21.878', '128', 'Medium'],
                ['3', 'Масса', 'Williams', '1.22.076', '103', 'Soft'],
                ['4', 'Магнуссен', 'Haas F1', '1.22.894', '51', 'Soft'],
                ['5', 'Риккардо', 'Red Bull Racing', '1.22.926', '50', 'Soft'],
                ['6', 'Боттас', 'Mercedes', '1.23.169', '79', 'Soft'],
                ['7', 'Перес', 'Force India', '1.23.709', '39', 'Soft'],
                ['8', 'Сайнс', 'Toro Rosso', '1.24.494', '51', 'Medium'],
                ['9', 'Хюлкенберг', 'Renault', '1.24.784', '57', 'Medium'],
                ['10', 'Алонсо', 'McLaren', '1.24.852', '29', 'Soft'],
                ['11', 'Эриксон', 'Sauber', '1.26.841', '72', 'Medium']
             ]
        ]
        self.assertEqual(expected, self._parser.results())

    def get_response_file_path(self):
        return 'responses/f1-news-testing-2017.html'

    def init_parser(self, html):
        return F1NewsTestingParser(html)


class TestF1NewsTeamPointsParser(TestParser):
    def test_points(self):
        expected = [
            ('1', 'Mercedes', '765'),
            ('2', 'Red Bull', '468'),
            ('3', 'Ferrari', '398'),
            ('4', 'Force India', '173'),
            ('5', 'Williams', '138'),
            ('6', 'McLaren', '76'),
            ('7', 'Toro Rosso', '63'),
            ('8', 'Haas', '29'),
            ('9', 'Renault', '8'),
            ('10', 'Sauber', '2'),
            ('11', 'Manor', '1'),
        ]
        self.assertEqual(expected, self._parser.points())

    def get_response_file_path(self):
        return 'responses/f1-news-team-points-2016.html'

    def init_parser(self, html):
        return F1NewsTeamPointsParser(html)


class TestF1NewsRaceCatalogParse(TestParser):
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


class TestF1NewsRaceResultParser(TestParser):
    def test_weather(self):
        expected = 'Облачно. Сухо. Воздух +16С, трасса +40...35С'
        self.assertEqual(expected, self._parser.weather())

    def test_points(self):
        expected = [
            ('1', 'Росберг', '100'),
            ('2', 'Хэмилтон', '57'),
            ('3', 'Райкконен', '43'),
            ('4', 'Риккардо', '36'),
            ('5', 'Феттель', '33'),
            ('6', 'Масса', '32'),
            ('7', 'Грожан', '22'),
            ('8', 'Квят', '21'),
            ('9', 'Боттас', '19'),
            ('10', 'Ферстаппен', '13'),
            ('11', 'Алонсо', '8'),
            ('12', 'Магнуссен', '6'),
            ('13', 'Хюлкенберг', '6'),
            ('14', 'Сайнс', '4'),
            ('15', 'Перес', '2'),
            ('16', 'Баттон', '1'),
            ('17', 'Вандорн', '1'),
        ]
        self.assertEqual(expected, self._parser.points())

    def test_results(self):
        expected = [
            ('1', 'Росберг', 'Mercedes', '200.482'),
            ('2', 'Хэмилтон', 'Mercedes', '199.584'),
            ('3', 'Райкконен', 'Ferrari', '199.335'),
            ('4', 'Боттас', 'Williams', '198.688'),
            ('5', 'Масса', 'Williams', '197.834'),
            ('6', 'Алонсо', 'McLaren', '196.587'),
            ('7', 'Магнуссен', 'Renault', '196.282'),
            ('8', 'Грожан', 'Haas', '196.213'),
            ('9', 'Перес', 'Force India', '196.160'),
            ('10', 'Баттон', 'McLaren', '196.021'),
            ('11', 'Риккардо', 'Red Bull', '195.752'),
            ('12', 'Сайнс', 'Toro Rosso', '195.429'),
            ('13', 'Палмер', 'Renault', '195.428'),
            ('14', 'Эриксон', 'Sauber', '195.359'),
            ('15', 'Квят', 'Red Bull', '194.815'),
            ('16', 'Наср', 'Sauber', '194.586'),
            ('17', 'Гутьеррес', 'Haas', '194.340'),
            ('18', 'Верляйн', 'Manor', '191.625'),
            (None, 'Ферстаппен', 'Toro Rosso', None),
            (None, 'Харьянто', 'Manor', None),
            (None, 'Хюлкенберг', 'Force India', None),
            (None, 'Феттель', 'Ferrari', None),
        ]
        self.assertEqual(expected, self._parser.results())

    def get_response_file_path(self):
        return 'responses/f1-news-race-4-2016.html'

    def init_parser(self, html):
        return F1NewsRaceResultParser(html)


if __name__ == '__main__':
    unittest.main()
