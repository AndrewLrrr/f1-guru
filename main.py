import logging
import os
import sys
from collections import defaultdict

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


SCRAPERS = {
    'f1news.ru': Scraper('f1news.ru', protocol='https'),
}

PROXY_SCRAPERS = {
    'f1news.ru': ProxyScraper('f1news.ru', protocol='https'),
}

YEARS_PERIOD = (2014, 2015, 2016, 2017, 2018)

TEAMS_MAPPING = {
    'Mercedes': 'Mercedes',
    'Ferrari': 'Ferrari',
    'Williams': 'Williams',
    'Haas F1': 'Haas',
    'Haas': 'Haas',
    'Red Bull Racing': 'Red Bull',
    'Red Bull': 'Red Bull',
    'Force India': 'Force India',
    'Toro Rosso': 'Toro Rosso',
    'Renault': 'Toro Rosso',
    'McLaren': 'McLaren',
    'Sauber': 'Sauber',
    'Lotus': 'Lotus',
    'Manor': 'Manor',
    'Marussia': 'Marussia',
    'Caterham': 'Caterham',
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
    'driver',
    'finish_position',
    'start_position',
    'average_finish_position',
    'average_speed',
    'lag_from_the_leader',
    'lag_from_the_next',
    'team',
    'weather',
    'laps',
    'points',

)

TESTING_RESULTS_HEADERS = ('day', 'year', 'track', 'position', 'time', 'laps', 'tyres', 'team')

TEAMS_DATA_HEADERS = ('team', 'engine', 'team_leader', 'technical_director', 'budget', 'is_factory_team')

TEAM_POINTS_HEADERS = ('position', 'team', 'points')


@decorators.save_to_cache('scraped_data')
def scrape_data(scraper_code, uri, params=None, headers=None):
    scrapers_source = PROXY_SCRAPERS if settings.USE_PROXY else SCRAPERS
    scraper = scrapers_source.get(scraper_code)
    if not scraper:
        raise ValueError('Scraper for site `{}` does not exist'.format(scraper))
    return scraper.scrape(uri, params=params, headers=headers)


def join_laps(results):
    extra_rows = []
    for idx1, r1 in enumerate(results):
        for idx2, r2 in enumerate(results):
            if r1[1] != r2[1] and r1[2] == r2[2] and idx1 not in extra_rows:
                r1[4] = int(r1[4]) + int(r2[4])
                extra_rows.append(idx2)
    for extra_row in sorted(extra_rows, reverse=True):
        del results[extra_row]
    return results


def get_testing_results(year, source='f1news.ru'):
    total = []
    day = 1
    for uri in TESTING_URI[source][year]:
        data = scrape_data(source, uri)
        parser = F1NewsTestingParser(data)
        track = parser.track()
        all_results = parser.results()
        for results in reversed(all_results):
            results = join_laps(results)
            for result in results:
                pos, driver, team, time, laps, tyres = result
                total.append((
                    day,
                    year,
                    track,
                    int(pos),
                    time,
                    laps,
                    tyres,
                    TEAMS_MAPPING[team],
                ))
            day += 1
    return total


def get_race_results(year, source='f1news.ru'):
    race_results = []
    catalog_data = scrape_data(source, RACING_CATALOGS_URI[source][year])
    parser = F1NewsRaceCatalogParser(catalog_data)
    uris = parser.links()
    tracks = parser.tracks()
    laps = parser.laps()
    positions = defaultdict(list)
    for i, uri in enumerate(uris):
        start_positions_uri = uri.replace('race.shtml', 'grid.shtml')
        race_parser = load_race_results_by_uri(uri, source=source)
        start_positions_parser = load_race_starting_positions_by_uri(start_positions_uri, source=source)
        total = []
        weather = race_parser.weather().split('.')[1].strip()
        results = race_parser.results()
        points = race_parser.points()
        start_positions = start_positions_parser.positions()
        leader_speed = 0
        prev_speed = 0.0
        diff_prev_speed = 0.0
        diff_leader_speed = 0.0
        for j in range(len(results)):
            pos, driver, team, average_speed, retire_lap = results[j]
            if pos == 'DQ':
                continue
            average_speed = float(average_speed) if average_speed else None
            if j == 0:
                leader_speed = average_speed
                prev_speed = average_speed
            else:
                diff_prev_speed = round(prev_speed - average_speed, 3) if average_speed else None
                diff_leader_speed = round(leader_speed - average_speed, 3) if average_speed else None
                prev_speed = average_speed
            driver = results[j][1]
            point = [p for p in points if p[1] == driver]
            point = int(point[0][2]) if point else 0
            start_position = [sp for sp in start_positions if sp[1] == driver]
            start_position = int(start_position[0][0]) if start_position and start_position[0][0] else None
            finish_position = j+1
            positions[driver].append(finish_position)
            result = []
            result.extend([
                i+1,
                year,
                tracks[i],
                driver,
                finish_position,
                start_position,
                sum(positions[driver]) / len(positions[driver]),  # Средняя позиция в гонке
                average_speed,
                diff_leader_speed,
                diff_prev_speed,
                team,
                weather,
                int(retire_lap) if retire_lap else int(laps[i]),
                point,
            ])
            total.append(result)
        race_results.extend(total)
    return race_results


def load_race_results_by_uri(uri, source='f1news.ru'):
    data = scrape_data(source, uri)
    return F1NewsRaceResultParser(data)


def load_race_starting_positions_by_uri(uri, source='f1news.ru'):
    data = scrape_data(source, uri)
    return F1NewsRaceStartingPositionsParser(data)


def get_team_points(year, source='f1news.ru'):
    data = scrape_data(source, TEAM_POINTS_URI[source][year])
    parser = F1NewsTeamPointsParser(data)
    return parser.points()


def build_testing_data_sets(year):
    results_df = pd.DataFrame(get_testing_results(year), columns=TESTING_RESULTS_HEADERS)
    if year != 2018:
        points_df = pd.DataFrame(get_team_points(year), columns=TEAM_POINTS_HEADERS)[['team', 'points']]
        points_df['points'] = points_df['points'].astype(float)
        results_df = results_df.merge(points_df, on='team').sort_values(['day', 'time', 'points'])
    return results_df


def build_racing_data_sets(year):
    return pd.DataFrame(get_race_results(year), columns=RACING_RESULTS_HEADERS)


def build_team_data_sets(year):
    df = pd.DataFrame(list(TEAMS_ADDITIONAL_DATA[year]), columns=TEAMS_DATA_HEADERS)
    df['year'] = year
    return df


def save_data_frame_as_csv(df, period, prefix):
    if len(period) > 1:
        path = '{}-data-{}-{}.csv'.format(prefix, period[0], period[-1])
    else:
        path = '{}-data-{}.csv'.format(prefix, period[0])
    full_path = os.path.join(settings.STORAGE_PATH, path)
    df.to_csv(full_path, encoding='utf-8', index=False)


def main():
    logger.info('Start building data set...')

    try:
        modes = [sys.argv[1]]
    except IndexError:
        modes = ('testing', 'racing', 'team',)

    try:
        current_year = int(sys.argv[2])
        if current_year < YEARS_PERIOD[0] or current_year > YEARS_PERIOD[-1]:
            raise ValueError('Year should be between {} and {}'.format(YEARS_PERIOD[0], YEARS_PERIOD[-1]))
    except IndexError:
        current_year = None

    if not current_year:
        period = YEARS_PERIOD[:-1]  # 2018 год не добавляем в выборку
    else:
        period = [current_year]

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
