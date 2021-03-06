import re

from helpers.helpers import add_milliseconds_to_time
from parsers.parser import Parser


COLUMNS = ('пилот|гонщик', 'команда', 'время', 'круги', 'шины',)


class F1NewsTestingParser(Parser):
    def dates(self):
        return [t.text for t in self._soup.find_all('h3') if re.match('^\d', t.text)]

    def track(self):
        return self._soup.find('h1').text.split('.')[-1].strip()

    def results(self):
        tables = self._soup.find_all('table', {'class': 'f1Table'})
        results = []
        for table in tables:
            headers = [td.text for td in table.find('tr', {'class': 'firstLine'}).find_all('td')]
            need_correct_lap_time = False
            mapping = []

            # Указываем по какому индексу брать нужные данные из таблицы
            for column in COLUMNS:
                num = None
                find_column = False
                for idx, header in enumerate(headers):
                    if column.find('|') != -1:
                        if header.lower() in column.split('|'):
                            find_column = True
                    else:
                        if header.lower() == column:
                            find_column = True
                    if find_column:
                        num = idx
                        break
                mapping.append(num)

            rows = table.find_all('tr', {'class': ['lineOne', 'lineTwo']})
            result = []
            for row in rows:
                row = row.find_all('td')
                line = []
                for i in mapping:
                    if i is not None:
                        if i == 0:
                            pos, _, racer = [i.strip() for i in row[i].text.split('.') if i]
                            line.extend([pos, racer])
                        else:
                            if row[i].text.startswith('+'):
                                need_correct_lap_time = True
                            line.append(self._normalize(row[i].text))
                    else:
                        line.append(None)
                result.append(line)
            if need_correct_lap_time:
                result = self._normalize_lap_times(result)
            results.append(result)
        return results

    @staticmethod
    def _normalize(item):
        item = item.strip()
        if item.find('без времени') != -1 or not item:
            return None
        if item.startswith('+'):
            item = item.replace('+', '')
        return item.replace(':', '.').replace('\'', '.').replace('"', '.')

    @staticmethod
    def _normalize_lap_times(results):
        best_lap_time = results[0][3]
        for i in range(1, len(results), 1):
            sec, ms = [int(r) for r in results[i][3].split('.')]
            results[i][3] = add_milliseconds_to_time(best_lap_time, (sec * 1000 + ms))
        return results
