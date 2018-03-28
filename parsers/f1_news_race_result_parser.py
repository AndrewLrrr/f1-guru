import re

from parsers.parser import Parser


class F1NewsRaceResultParser(Parser):
    def results(self):
        tables = self._soup.find_all('table', {'class': 'f1Table'})
        results_table = tables[0]
        descent_table = tables[1]
        results = []
        rows = results_table.find_all('tr', {'class': ['lineOne', 'lineTwo']})
        for row in rows:
            row = row.find_all('td')
            pos, _, driver = [s.replace('*', '').strip() for s in row[0].text.split('.')]
            team = row[1].text
            speed = row[3].text
            results.append((pos, driver, team, speed, None))
        # Добавляем сошедших гонщиков
        rows = descent_table.find_all('tr', {'class': ['lineOne', 'lineTwo']})
        first_ret_lap = int(rows[0].find_all('td')[2].text)
        last_ret_lap = int(rows[-1].find_all('td')[2].text)
        if first_ret_lap < last_ret_lap:
            rows = reversed(rows)
        for row in rows:
            row = row.find_all('td')
            _, driver = [s.strip() for s in row[0].text.split('.')]
            team = row[1].text
            retire_lap = row[2].text

            results.append((None, driver, team, None, retire_lap))
        return results

    def weather(self):
        return self._soup.find('span', {'class': 'subInfo'}).text

    def points(self):
        table = self._soup.find_all('table', {'class': 'f1Table'})[2]
        results = []
        rows = table.find_all('tr', {'class': ['lineOne', 'lineTwo']})
        for row in rows:
            row = row.find_all('td')
            if not re.search('^\d+\..*', row[1].text):
                text = row[0].text
            else:
                text = row[1].text
            parts = [s.strip() for s in text.split('.')]
            pos = parts[0]
            driver = parts[-1]
            points = row[-1].text
            results.append((pos, driver, points))
        return results
