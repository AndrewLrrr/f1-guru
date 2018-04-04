import logging
import os
import sys
from collections import defaultdict, namedtuple

import pandas as pd

import settings
from decorators import decorators
from helpers.scraper import ProxyScraper, Scraper
from parsers.f1_news_race_calatog_parser import F1NewsRaceCatalogParser
from parsers.f1_news_race_result_parser import F1NewsRaceResultParser
from parsers.f1_news_race_starting_positions_parser import F1NewsRaceStartingPositionsParser
from parsers.f1_news_team_points_parser import F1NewsTeamPointsParser
from parsers.f1_news_testing_parser import F1NewsTestingParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ------------------------------------------------- Constants Block -------------------------------------------------- #


SCRAPERS = {
    'f1news.ru': Scraper('f1news.ru', protocol='https'),
}

PROXY_SCRAPERS = {
    'f1news.ru': ProxyScraper('f1news.ru', protocol='https'),
}

PARSERS = {
    'f1news.ru': {
        'race_catalog': F1NewsRaceCatalogParser,
        'race_results': F1NewsRaceResultParser,
        'race_starting_positions': F1NewsRaceStartingPositionsParser,
        'team_points': F1NewsTeamPointsParser,
        'testing': F1NewsTestingParser,
    }
}

YEARS_PERIOD = (2014, 2015, 2016, 2017, 2018)

TEAMS_MAPPING = {
    'Mercedes': 'Mercedes',
    'Ferrari': 'Ferrari',
    'Williams': 'Williams',
    'Haas F1': 'Haas',
    'Haas': 'Haas',
    'Red Bull': 'Red Bull',
    'Force India': 'Force India',
    'Toro Rosso': 'Toro Rosso',
    'Renault': 'Renault',
    'McLaren': 'McLaren',
    'Sauber': 'Sauber',
    'Lotus': 'Lotus',
    'Manor': 'Manor',
    'Marussia': 'Marussia',
    'Caterham': 'Caterham',
    'Red Bull Racing': 'Red Bull',
    'Red Bull/Renault': 'Red Bull',
    'Williams/Mercedes': 'Williams',
    'Sauber/Ferrari': 'Sauber',
    'Force India/Mercedes': 'Force India',
    'Toro Rosso/Renault': 'Toro Rosso',
    'McLaren/Honda': 'McLaren',
    'МсLaren': 'McLaren',
}

TYRES_MAPPING = {
    'SSoft': 'SuperSoft',
}

TRACKS_MAPPING = {
    'Марина-Бей': 'Сингапур',
    'Альберт-парк': 'Мельбурн',
}

WEATHER_MAPPING = {
    'Сухо': 'dry',
    'Подсыхающая трасса': 'changeable',
    'Дождь': 'wet',
    'Дождь в конце гонки': 'changeable',
    'облачность': 'dry',
    'Дождь, в конце сухо': 'changeable',
}

# Дополнительные данные будем записывать в формате:
# Двигатель, Руководитель, Тех.директор, Бюджет (в млн евро), Официальная поддержка от моториста
TEAMS_ADDITIONAL_DATA = {
    2014: (
        ('Mercedes', 'Mercedes', 'Тото Вольфф', 'Падди Лоу', 300, 1),
        ('Ferrari', 'Ferrari', 'Марко Маттиаччи', 'Джеймс Эллисон', 410, 1),
        ('Red Bull', 'Renault', 'Кристиан Хорнер', 'Эдриан Ньюи', 425, 1),
        ('Williams', 'Mercedes', 'Клэр Уильямс', 'Пэт Симондс', 150, 0),
        ('Force India', 'Mercedes', 'Роберт Фернли', 'Энди Грин', 75, 0),
        ('Toro Rosso', 'Renault', 'Франц Тост', 'Джеймс Ки', 80, 0),
        ('Lotus', 'Renault', 'Жерар Лопес', 'Ник Честер', 160, 0),
        ('McLaren', 'Mercedes', 'Эрик Булье', 'Тим Госс', 230, 0),
        ('Sauber', 'Ferrari', 'Мониша Кальтенборн', 'Эрик Ганделин', 85, 0),
        ('Marussia', 'Ferrari', 'Джон Бут', 'Джон МакКиллиам', 60, 0),
        ('Caterham', 'Renault', 'Сирил Абитебул', 'Марк Смит', 70, 0),
    ),
    2015: (
        ('Mercedes', 'Mercedes', 'Тото Вольфф', 'Падди Лоу', 230 * 1.35, 1),
        ('Ferrari', 'Ferrari', 'Маурицио Арривабене', 'Джеймс Эллисон', 225 * 1.35, 1),
        ('Red Bull', 'Renault', 'Кристиан Хорнер', 'Эдриан Ньюи', 200 * 1.35, 1),
        ('Williams', 'Mercedes', 'Клэр Уильямс', 'Пэт Симондс', 110 * 1.35, 0),
        ('Force India', 'Mercedes', 'Роберт Фернли', 'Энди Грин', 110 * 1.35, 0),
        ('Toro Rosso', 'Renault', 'Франц Тост', 'Джеймс Ки', 90 * 1.35, 0),
        ('Lotus', 'Renault', 'Жерар Лопес', 'Ник Честер', 100 * 1.35, 0),
        ('McLaren', 'Honda', 'Эрик Булье', 'Тим Госс', 180 * 1.35, 1),
        ('Sauber', 'Ferrari', 'Мониша Кальтенборн', 'Эрик Ганделин', 90 * 1.35, 0),
        ('Manor', 'Ferrari', 'Джон Бут', 'Джон МакКиллиам', 60 * 1.35, 0),
    ),
    2016: (
        ('Mercedes', 'Mercedes', 'Тото Вольфф', 'Падди Лоу', 265 * 1.20, 1),
        ('Ferrari', 'Ferrari', 'Маурицио Арривабене', 'Джеймс Эллисон', 330 * 1.20, 1),
        ('Red Bull', 'Renault', 'Кристиан Хорнер', 'Эдриан Ньюи', 215 * 1.20, 0),
        ('Williams', 'Mercedes', 'Клэр Уильямс', 'Пэт Симондс', 105 * 1.20, 0),
        ('Force India', 'Mercedes', 'Роберт Фернли', 'Энди Грин', 90 * 1.20, 0),
        ('Toro Rosso', 'Renault', 'Франц Тост', 'Джеймс Ки', 100 * 1.20, 0),
        ('Renault', 'Renault', 'Сирил Абитебул', 'Ник Честер', 150 * 1.20, 1),
        ('McLaren', 'Honda', 'Эрик Булье', 'Тим Госс', 185 * 1.20, 1),
        ('Sauber', 'Ferrari', 'Мониша Кальтенборн', 'Эрик Ганделин', 95 * 1.20, 0),
        ('Manor', 'Ferrari', 'Дэйв Райан', 'Джон МакКиллиам', 85 * 1.20, 0),
        ('Haas', 'Ferrari', 'Гюнтер Штайнер', 'Роб Тэйлор', 100 * 1.20, 0),
    ),
    2017: (
        ('Mercedes', 'Mercedes', 'Тото Вольфф', 'Джеймс Эллисон', 310, 1),
        ('Ferrari', 'Ferrari', 'Маурицио Арривабене', 'Маттиа Бинотто', 260, 1),
        ('Red Bull', 'Renault', 'Кристиан Хорнер', 'Эдриан Ньюи', 250, 0),
        ('Williams', 'Mercedes', 'Клэр Уильямс', 'Падди Лоу', 120, 0),
        ('Force India', 'Mercedes', 'Роберт Фернли', 'Энди Грин', 109, 0),
        ('Toro Rosso', 'Renault', 'Франц Тост', 'Джеймс Ки', 115, 0),
        ('Renault', 'Renault', 'Сирил Абитебул', 'Ник Честер', 172, 1),
        ('McLaren', 'Honda', 'Эрик Булье', 'Тим Госс', 212, 1),
        ('Sauber', 'Ferrari', 'Мониша Кальтенборн', 'Йорг Цандер', 109, 0),
        ('Haas', 'Ferrari', 'Гюнтер Штайнер', 'Роб Тэйлор', 115, 0),
    ),
    2018: (
        ('Mercedes', 'Mercedes', 'Тото Вольфф', 'Джеймс Эллисон', 450, 1),
        ('Ferrari', 'Ferrari', 'Маурицио Арривабене', 'Маттиа Бинотто', 430, 1),
        ('Red Bull', 'Renault', 'Кристиан Хорнер', 'Эдриан Ньюи', 350, 0),
        ('Williams', 'Mercedes', 'Клэр Уильямс', 'Падди Лоу', 135, 0),
        ('Force India', 'Mercedes', 'Роберт Фернли', 'Энди Грин', 110, 0),
        ('Toro Rosso', 'Honda', 'Франц Тост', 'Джеймс Ки', 125, 1),
        ('Renault', 'Renault', 'Сирил Абитебул', 'Ник Честер', 200, 0),
        ('McLaren', 'Renault', 'Эрик Булье', 'Тим Госс', 250, 1),
        ('Sauber', 'Ferrari', 'Мониша Кальтенборн', 'Йорг Цандер', 135, 0),
        ('Haas', 'Ferrari', 'Гюнтер Штайнер', 'Роб Тэйлор', 110, 0),
    ),
}

TESTING_URI = {
    'f1news.ru': {
        2014: (
            'Championship/2014/tests/91918.shtml',
            'Championship/2014/tests/92316.shtml',
            'Championship/2014/tests/92545.shtml',
        ),
        2015: (
            'Championship/2015/tests/100942.shtml',
            'Championship/2015/tests/101278.shtml',
            'Championship/2015/tests/101460.shtml',
        ),
        2016: (
            'Championship/2016/tests/110193.shtml',
            'Championship/2016/tests/110425.shtml',
        ),
        2017: (
            'Championship/2017/tests/118950.shtml',
            'Championship/2017/tests/119022.shtml',
            'Championship/2017/tests/119147.shtml',
        ),
        2018: (
            'Championship/2018/tests/127142.shtml',
            'Championship/2018/tests/127171.shtml',
            'Championship/2018/tests/127211.shtml',
            'Championship/2018/tests/127236.shtml',
            'Championship/2018/tests/127333.shtml',
            'Championship/2018/tests/127370.shtml',
            'Championship/2018/tests/127402.shtml',
            'Championship/2018/tests/127438.shtml',
        ),
    }
}

RACING_CATALOGS_URI = {
    'f1news.ru': {
        2013: 'Championship/2013/',
        2014: 'Championship/2014/',
        2015: 'Championship/2015/',
        2016: 'Championship/2016/',
        2017: 'Championship/2017/',
        2018: 'Championship/2018/',
    }
}

TEAM_POINTS_URI = {
    'f1news.ru': {
        2014: 'Championship/2014/teampoints.shtml',
        2015: 'Championship/2015/teampoints.shtml',
        2016: 'Championship/2016/teampoints.shtml',
        2017: 'Championship/2017/teampoints.shtml',
    }
}

RACING_RESULTS_HEADERS = (
    'number',
    'year',
    'track',
    'laps',
    'points',
    'driver',
    'finish_position',
    'start_position',
    'average_finish_position',
    'average_speed',
    'lag_from_the_leader',
    'lag_from_the_next',
    'team',
    'weather',
    'finish_position_prev',
    'start_position_prev',
    'average_finish_position_prev',
    'average_speed_prev',
    'lag_from_the_leader_prev',
    'lag_from_the_next_prev',
    'team_prev',
    'weather_prev',
)

TESTING_RESULTS_HEADERS = ('day', 'year', 'track', 'position', 'time', 'laps', 'tyres', 'team')

TEAMS_DATA_HEADERS = ('team', 'engine', 'team_leader', 'technical_director', 'budget', 'is_factory_team')

TEAM_POINTS_HEADERS = ('position', 'team', 'points')


# -------------------------------------------------- Helpers Block --------------------------------------------------- #


@decorators.save_to_cache('scraped_data')
def scrape_data(scraper_code, uri, params=None, headers=None):
    """
    Загружает заданную станицу сайта и кеширует ее для повторных запросов
    :param str scraper_code: Источник данных
    :param str uri: Uri
    :param dict params: Дополнительные параметры запроса
    :param dict headers: Дополнительные заголовки запроса
    :return: str
    """
    scrapers_source = PROXY_SCRAPERS if settings.USE_PROXY else SCRAPERS
    scraper = scrapers_source.get(scraper_code)
    if not scraper:
        raise ValueError('Scraper for site `{}` does not exist'.format(scraper))
    return scraper.scrape(uri, params=params, headers=headers)


# ------------------------------------------------ Test Results Block ------------------------------------------------ #


def join_team_results(results):
    """
    Объединяет результаты всех гонщиков одной команды за тестовый день, 
    оставляет в списке лучший результат, а также общую сумму пройденных кругов
    :param results: Список результатов тестов за день
    :return: list
    """
    extra_rows = []
    for idx1, r1 in enumerate(results):
        for idx2, r2 in enumerate(results):
            if r1[1] != r2[1] and r1[2] == r2[2] and idx1 not in extra_rows:
                r1[4] = int(r1[4]) + int(r2[4])
                extra_rows.append(idx2)
    for extra_row in sorted(extra_rows, reverse=True):
        del results[extra_row]
    return results


def get_team_points(year, source='f1news.ru'):
    """
    Загружает, парсит и возвращает итоговое количество очков в кубке конструкторов (результаты команд)
    :param year: Год проведения чемпионата
    :param source: Источник данных
    :return: list
    """
    data = scrape_data(source, TEAM_POINTS_URI[source][year])
    parser = PARSERS[source]['team_points'](data)
    return parser.points()


def get_testing_results(year, source='f1news.ru'):
    """
    Собирает результаты всех зимних тестов за сезон, считает дополнительные статистики
    :param year: Год проведения чемпионата
    :param source: Источник данных
    :return: 
    """
    total = []
    day = 1
    for uri in TESTING_URI[source][year]:
        data = scrape_data(source, uri)
        parser = PARSERS[source]['testing'](data)
        track = parser.track()
        all_results = parser.results()
        for results in reversed(all_results):
            results = join_team_results(results)
            for result in results:
                pos, driver, team, time, laps, tyres = result
                total.append((
                    day,
                    year,
                    track if track not in TRACKS_MAPPING else TRACKS_MAPPING[track],
                    int(pos),
                    time,
                    laps,
                    tyres if tyres not in TYRES_MAPPING else TYRES_MAPPING[tyres],
                    TEAMS_MAPPING[team.strip()],
                ))
            day += 1
    return total


# ------------------------------------------------ Race Results Block ------------------------------------------------ #


def rebuild_race_results_with_disqualified_drivers(results):
    """
    Перестраивает результаты гонки если там есть дисквалифицированные гонщики, 
    в таком случае, данный гонщик извлекается из списка и добавляется в самый конец 
    итогового протокола, остальные, соответсвенно, поднимаются на одну позицию вверх
    :param results: Результаты гонки
    :return: list
    """
    new_res = []
    disqualified = []
    counter = 1
    for pos, driver, team, average_speed, retire_lap in results:
        if pos == 'DQ':
            disqualified.append([driver, team, average_speed, retire_lap])
        else:
            new_res.append((counter, driver, team, average_speed, retire_lap))
            counter += 1
    for driver, team, average_speed, retire_lap in disqualified:
        new_res.append((counter, driver, team, average_speed, retire_lap))
        counter += 1
    return new_res


def fill_start_positions_na(positions):
    """
    Заполняет пустые стартовые позиции (в случае старта с пит-лейна или других проблем у гонщика)
    :param positions: Список стартовых позиций
    :return: list
    """
    PositionsData = namedtuple('PositionsData', ['pos', 'driver', 'time'])
    result = []
    for i, item in enumerate(positions):
        pos, driver, time = item
        result.append(PositionsData(*[i+1, driver, time]))
    return result


def get_race_results_by_uri(uri, source='f1news.ru'):
    """
    Собирает результаты гонки по uri, парсит и формирует заданный результат
    :param uri: Uri
    :param source: Источник данных
    :return: list
    """
    race_results = []
    RaceData = namedtuple(
        'RaceData',
        [
            'driver',
            'finish_position',
            'start_position',
            'average_speed',
            'diff_leader_speed',
            'diff_prev_speed',
            'retire_lap',
            'points',
            'team',
            'weather',
        ]
    )
    start_positions_uri = uri.replace('race.shtml', 'grid.shtml')
    race_parser = load_race_results_by_uri(uri, source=source)
    start_positions_parser = load_race_starting_positions_by_uri(start_positions_uri, source=source)
    weather = race_parser.weather().split('.')[1].strip()
    results = rebuild_race_results_with_disqualified_drivers(race_parser.results())
    points = race_parser.points()
    start_positions = fill_start_positions_na(start_positions_parser.positions())
    leader_speed = 0.0
    prev_speed = 0.0
    diff_prev_speed = 0.0
    diff_leader_speed = 0.0
    for j in range(len(results)):
        pos, driver, team, average_speed, retire_lap = results[j]
        average_speed = float(average_speed) if average_speed else None
        if j == 0:
            leader_speed = average_speed
            prev_speed = average_speed
        else:
            if average_speed:
                diff_prev_speed = round(prev_speed - average_speed, 3) if prev_speed else None
                diff_leader_speed = round(leader_speed - average_speed, 3) if leader_speed else None
            else:
                diff_prev_speed = None
                diff_leader_speed = None
            prev_speed = average_speed
        driver = results[j][1]
        point = [p for p in points if p[1] == driver]
        point = int(point[0][2]) if point else 0
        last_start_position = max([sp.pos for sp in start_positions]) + 1
        start_position = [sp for sp in start_positions if sp.driver == driver]
        start_position = start_position[0].pos if start_position else None
        if not start_position:
            start_position = last_start_position
            last_start_position += 1
        result = RaceData(*[
            driver,
            pos,
            start_position,
            average_speed,
            diff_leader_speed,
            diff_prev_speed,
            int(retire_lap) if retire_lap else None,
            point,
            TEAMS_MAPPING[team.strip()],
            WEATHER_MAPPING[weather],
        ])
        race_results.append(result)
    return race_results


def get_all_race_results(year, source='f1news.ru'):
    """
    Собирает результаты всех гонок за сезон, считает дополнительные статистики
    :param year: Год проведения чемпионата
    :param source: Источник данных
    :return: list
    """
    RaceData = namedtuple(
        'RaceData',
        [
            'number',
            'year',
            'track',
            'driver',
            'finish_position',
            'start_position',
            'average_finish_position',
            'average_finish_position_prev',
            'average_speed',
            'diff_leader_speed',
            'diff_prev_speed',
            'team',
            'weather',
            'laps',
            'points',
        ]
    )
    all_race_results = []
    catalog_data = scrape_data(source, RACING_CATALOGS_URI[source][year])
    parser = PARSERS[source]['race_catalog'](catalog_data)
    uris = parser.links()
    tracks = parser.tracks()
    laps = parser.laps()
    positions = defaultdict(list)
    for i, uri in enumerate(uris):
        total_result = []
        race_result = get_race_results_by_uri(uri, source)
        for result in race_result:
            positions[result.driver].append(result.finish_position)
            track = tracks[i]
            average_finish_position = sum(positions[result.driver]) / len(positions[result.driver])
            try:
                average_finish_position_prev = sum(positions[result.driver][:-1]) / len(positions[result.driver][:-1])
            except ZeroDivisionError:
                average_finish_position_prev = 0
            total_result.append(RaceData(*[
                i+1,
                year,
                track if track not in TRACKS_MAPPING else TRACKS_MAPPING[track],
                result.driver,
                result.finish_position,
                result.start_position,
                average_finish_position,       # Средняя позиция в гонке на текущий момент
                average_finish_position_prev,  # Средняя позиция в гонке на момент предыдущей гонки
                result.average_speed,
                result.diff_leader_speed,
                result.diff_prev_speed,
                result.team,
                result.weather,
                result.retire_lap if result.retire_lap else laps[i],
                result.points,
            ]))
        all_race_results.append(total_result)
    return merge_race_results_with_prev(all_race_results, year, source=source)


def merge_race_results_with_prev(all_race_results, year, source='f1news.ru'):
    """
    Объединяет результаты для каждой гонки чемпионата с предыдущей 
    (если эта первая гонка, то берем результаты последней за прошлый год)
    :param all_race_results: Результаты всех гонок чемпионата
    :param year: Год проведения чемпионата
    :param source: Источник данных
    :return: list
    """
    merged_all_race_results = []
    for idx, result in enumerate(all_race_results):
        if idx == 0:
            catalog_data = scrape_data(source, RACING_CATALOGS_URI[source][year-1])
            uris = PARSERS[source]['race_catalog'](catalog_data).links()
            prev_result = get_race_results_by_uri(uris[-1], source=source)
        else:
            prev_result = all_race_results[idx-1]
        for row1 in result:
            # Устанавливаем значения по умолчанию
            driver_has_been_found = False
            finish_position_prev = None
            start_position_prev = None
            average_speed_prev = None
            diff_leader_speed_prev = None
            diff_prev_speed_prev = None
            weather_prev = None
            team_prev = None
            # Сначала ищем совпадения по имени гонщика
            for row2 in prev_result:
                if row1.driver == row2.driver:
                    driver_has_been_found = True
                    finish_position_prev = row2.finish_position
                    start_position_prev = row2.start_position
                    average_speed_prev = row2.average_speed
                    diff_leader_speed_prev = row2.diff_leader_speed
                    diff_prev_speed_prev = row2.diff_prev_speed
                    weather_prev = row2.weather
                    team_prev = row2.team
            # Если по имени гонщика ничего не найдено, то скорее всего этот гонщик дебютант чемпионата,
            # поэтому ищем совпадения по названию команды
            if not driver_has_been_found:
                for row2 in prev_result:
                    if row1.team == row2.team and row1.driver != row2.driver:
                        finish_position_prev = row2.finish_position
                        start_position_prev = row2.start_position
                        average_speed_prev = row2.average_speed
                        diff_leader_speed_prev = row2.diff_leader_speed
                        diff_prev_speed_prev = row2.diff_prev_speed
                        weather_prev = row2.weather
                        team_prev = row2.team
            # TODO: Данная логика не учитывает появление новой команды в чемпионате, в текущем (2018) году таких
            # TODO: команд нет, но если такие появятся в будущем, подумать, что с этим можно сделать.
            merged_all_race_results.append([
                row1.number,
                row1.year,
                row1.track,
                row1.laps,
                row1.points,
                row1.driver,
                row1.finish_position,
                row1.start_position,
                row1.average_finish_position,
                row1.average_speed,
                row1.diff_leader_speed,
                row1.diff_prev_speed,
                row1.team,
                row1.weather,
                finish_position_prev,
                start_position_prev,
                row1.average_finish_position_prev,
                average_speed_prev,
                diff_leader_speed_prev,
                diff_prev_speed_prev,
                team_prev,
                weather_prev,
            ])
    return merged_all_race_results


def load_race_results_by_uri(uri, source='f1news.ru'):
    """
    Загружает результаты гонки по заданному uri и инициализирует соответсвующий парсер
    :param uri: Uri
    :param source: Источник данных
    :return: Parser
    """
    data = scrape_data(source, uri)
    return PARSERS[source]['race_results'](data)


def load_race_starting_positions_by_uri(uri, source='f1news.ru'):
    """
    Загружает результаты квалификации по заданному uri и инициализирует соответсвующий парсер
    :param uri: Uri
    :param source: Источник данных
    :return: Parser
    """
    data = scrape_data(source, uri)
    return PARSERS[source]['race_starting_positions'](data)


# --------------------------------------------- Data Sets Builders Block --------------------------------------------- #


def build_testing_data_sets(year):
    """
    Строит датафрейм на основе результатов тестов
    :param year: Год проведения чемпионата
    :return: pandas.DataFrame
    """
    df = pd.DataFrame(get_testing_results(year), columns=TESTING_RESULTS_HEADERS)
    if year != 2018:
        points_df = pd.DataFrame(get_team_points(year), columns=TEAM_POINTS_HEADERS)[['team', 'points']]
        points_df['points'] = points_df['points'].astype(float)
        df = df.merge(points_df, on='team').sort_values(['day', 'time', 'points'])
    return df


def build_racing_data_sets(year):
    """
    Строит датафрейм на основе результатов гонок
    :param year: Год проведения чемпионата
    :return: pandas.DataFrame
    """
    return pd.DataFrame(get_all_race_results(year), columns=RACING_RESULTS_HEADERS)


def build_team_data_sets(year):
    """
    Строит датафрейм на основе дополнительной информации о командах
    :param year: Год проведения чемпионата
    :return: pandas.DataFrame
    """
    df = pd.DataFrame(list(TEAMS_ADDITIONAL_DATA[year]), columns=TEAMS_DATA_HEADERS)
    df['year'] = year
    return df


def save_data_frame_as_csv(df, period, prefix):
    """
    Сохраняет датафрейм в виде csv файла
    :param df: pandas.DataFrame
    :param period: Период времени в годах [2014, 2017]
    :param prefix: Префикс имени файла
    """
    if len(period) > 1:
        path = '{}-data-{}-{}.csv'.format(prefix, period[0], period[-1])
    else:
        path = '{}-data-{}.csv'.format(prefix, period[0])
    full_path = os.path.join(settings.STORAGE_PATH, path)
    df.to_csv(full_path, encoding='utf-8', index=False)


# ---------------------------------------------------- Main Block ---------------------------------------------------- #


def main():
    logger.info('Start building data set...')

    try:
        modes = [sys.argv[1]]
    except IndexError:
        modes = ('testing', 'racing', 'team',)

    try:
        start_period = int(sys.argv[2])
        if start_period < YEARS_PERIOD[0] or start_period > YEARS_PERIOD[-1]:
            raise ValueError('Year should be between {} and {}'.format(YEARS_PERIOD[0], YEARS_PERIOD[-1]))
    except IndexError:
        start_period = None

    if not start_period:
        period = YEARS_PERIOD[:-1]  # 2018 год не добавляем в выборку по умолчанию
    else:
        period = [start_period]
        try:
            finish_period = int(sys.argv[3])
            if start_period < YEARS_PERIOD[0] or start_period > YEARS_PERIOD[-1]:
                raise ValueError('Year should be between {} and {}'.format(YEARS_PERIOD[0], YEARS_PERIOD[-1]))
            period = range(start_period, finish_period+1)
        except IndexError:
            pass

    for mode in modes:
        df = None
        if mode == 'testing':
            for year in period:
                if df is None:
                    df = build_testing_data_sets(year)
                else:
                    df = pd.concat([df, build_testing_data_sets(year)])
            save_data_frame_as_csv(df, period, 'testing')
        elif mode == 'racing':
            for year in period:
                if df is None:
                    df = build_racing_data_sets(year)
                else:
                    df = pd.concat([df, build_racing_data_sets(year)])
            save_data_frame_as_csv(df, period, 'racing')
        elif mode == 'team':
            for year in period:
                if df is None:
                    df = build_team_data_sets(year)
                else:
                    df = pd.concat([df, build_team_data_sets(year)])
            save_data_frame_as_csv(df, period, 'team')
        else:
            raise ValueError('Unsupported data set type `{}`'.format(mode))

    logger.info('Finish building data set')


if __name__ == '__main__':
    main()
