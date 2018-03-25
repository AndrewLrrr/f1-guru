import logging

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from decorators import decorators
from helpers.scraper import Scraper
from parsers.f1_news_team_points_parser import F1NewsTeamPointsParser
from parsers.f1_news_testing_parser import F1NewsTestingParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SCRAPERS = {
    'f1news.ru': Scraper('f1news.ru', protocol='https'),
}

YEARS_PERIOD = (2014, 2015, 2016, 2017, 2018,)

# Дополнительные данные будем записывать в формате:
# Двигатель, Руководитель, Тех.директор, Бюджет, Заводской статус
TEAMS_ADDITIONAL_DATA = {
    2014: (
        ('Mercedes',),
        ('Ferrari',),
        ('Williams',),
        ('Force India',),
        ('Toro Rosso',),
        ('Renault',),
        ('McLaren',),
        ('Sauber',),
        ('Haas',)
    ),
    2015: {},
    2016: {},
    2017: {},
    2018: {},
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

TESTING_RESULTS_HEADERS = ('position', 'team', 'time', 'laps', 'tyres', 'day')
TEAM_POINTS_HEADERS = ('position', 'team', 'points')


@decorators.save_to_cache('scraped_data')
def scrape_data(scraper_code, uri, params=None, headers=None):
    scraper = SCRAPERS.get(scraper_code)
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
    full_results = []
    day = 1
    for uri in TESTING_URI[source][year]:
        data = scrape_data(source, uri)
        parser = F1NewsTestingParser(data)
        all_results = parser.results()
        for results in reversed(all_results):
            results = join_laps(results)
            for result in results:
                result.append(day)
                full_results.append((
                    result[0],
                    result[2],
                    result[3],
                    result[4],
                    result[5],
                    day
                ))
            day += 1
    return full_results


def get_race_results(year):
    pass


def get_race_results_by_race_number(year, num):
    pass


def get_team_points(year, source='f1news.ru'):
    data = scrape_data(source, TEAM_POINTS_URI[source][year])
    parser = F1NewsTeamPointsParser(data)
    return parser.points()


def build_testing_data_sets(year):
    results_df = pd.DataFrame(get_testing_results(year), columns=TESTING_RESULTS_HEADERS)
    results_df['year'] = year
    if year != 2018:
        points_df = pd.DataFrame(get_team_points(year), columns=TEAM_POINTS_HEADERS)[['team', 'points']]
        scaler = MinMaxScaler()
        points_df['points'] = pd.DataFrame(
            scaler.fit_transform(points_df['points'].astype(float).values.reshape(-1, 1))
        )
        results_df = results_df.merge(points_df).sort_values(['day', 'time', 'points'])
        results_df.rename(columns={'points': 'strength'}, inplace=True)
    print(results_df.team.unique())
    print(results_df)
    return results_df


def build_racing_data_sets(year=None):
    return []


def save_as_csv(data, path):
    pass


def main():
    build_testing_data_sets(2017)
    # logger.info('Start building data set')
    #
    # mode = sys.argv.get(1)
    # year = sys.argv.get(2)
    #
    # if mode == 'testing':  # Make testing data set
    #     data = build_testing_data_sets(year)
    # elif mode == 'racing':  # Make racing data set
    #     data = build_racing_data_sets(year)
    # else:
    #     raise ValueError('Unsupported data set type `{}`'.format(mode))
    #
    # logger.info('Finish building data set')


if __name__ == '__main__':
    main()
