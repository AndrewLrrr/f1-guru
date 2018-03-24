import re

from helpers.helpers import add_milliseconds_to_time
from parsers.parser import Parser

# Указываем по какому индексу брать нужные данные из иаблицы
TABLE_TYPES_MAPPING = {
    1: (0, 1, 2, 4, None),
    2: (0, 1, 2, 4, 5),
    3: (0, 1, 2, 3, 4),
    4: (0, 1, 2, 4, None),
}


class F1NewsTestingParser(Parser):
    def dates(self):
        return [t.text for t in self._soup.find_all('h3') if re.match('^\d', t.text)]

    def results(self):
        tables = self._soup.find_all('table', {'class': 'f1Table'})
        results = []
        for table in tables:
            headers = [td.text for td in table.find('tr', {'class': 'firstLine'}).find_all('td')]
            need_correct_lap_time = False

            if len(headers) == 6 and 'Мотор' in headers:
                mapping = TABLE_TYPES_MAPPING[1]
            elif len(headers) == 5 and 'Шины' in headers:
                need_correct_lap_time = True
                mapping = TABLE_TYPES_MAPPING[3]
            elif len(headers) == 5:
                mapping = TABLE_TYPES_MAPPING[4]
            else:
                mapping = TABLE_TYPES_MAPPING[2]

            rows = table.find_all('tr', {'class': ['lineOne', 'lineTwo']})
            result = []
            for row in rows:
                row = row.find_all('td')
                line = []
                for i in mapping:
                    if i is not None:
                        if i == 0:
                            pos, _, racer = row[i].text.split('.')
                            line.extend([pos, racer])
                        else:
                            line.append(self._normalize(row[i].text))
                    else:
                        line.append(None)
                result.append(line)
            if need_correct_lap_time:
                result = self._normalize_lap_times(result)
            results.append(tuple(result))
        return results

    @staticmethod
    def _normalize(item):
        if item.find('без времени') != -1:
            return None
        if item.startswith('+'):
            item = item.replace('+', '')
        return item.replace(':', '.')

    @staticmethod
    def _normalize_lap_times(results):
        best_lap_time = results[0][3]
        for i in range(1, len(results), 1):
            sec, ms = [int(r) for r in results[i][3].split('.')]
            results[i][3] = add_milliseconds_to_time(best_lap_time, (sec * 1000 + ms))
        return results
