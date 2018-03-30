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
            driver_data = [s.replace('*', '').strip().strip('.') for s in row[0].text.split('.') if s.strip()]
            pos = driver_data[0]
            driver = driver_data[-1]
            if driver.find('-') != -1:
                driver = driver.split('-')[0]
            team = row[1].text
            speed = row[3].text
            results.append((pos, driver, team, speed, None))
        if len(tables) > 3:
            # Добавляем сошедших гонщиков
            rows = descent_table.find_all('tr', {'class': ['lineOne', 'lineTwo']})
            first_ret_lap = rows[0].find_all('td')[2].text
            last_ret_lap = rows[-1].find_all('td')[2].text
            first_ret_lap = 0 if first_ret_lap == 'нст' else int(first_ret_lap)
            last_ret_lap = 0 if last_ret_lap == 'нст' else int(last_ret_lap)
            if first_ret_lap < last_ret_lap:
                rows = reversed(rows)
            for row in rows:
                row = row.find_all('td')
                _, driver = [s.strip().strip('.') for s in row[0].text.split('.') if s.strip()]
                if driver.find('-') != -1:
                    driver = driver.split('-')[0]
                team = row[1].text
                retire_lap = '0' if row[2].text == 'нст' else row[2].text
                results.append((None, driver, team, None, retire_lap))
        return results

    def weather(self):
        return self._soup.find('span', {'class': 'subInfo'}).text

    def points(self):
        tables = self._soup.find_all('table', {'class': 'f1Table'})
        table = tables[2 if len(tables) > 3 else 1]
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
