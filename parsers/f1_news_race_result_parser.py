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
            results.append((pos, driver, team, speed))
        rows = descent_table.find_all('tr', {'class': ['lineOne', 'lineTwo']})
        for row in reversed(rows):
            row = row.find_all('td')
            _, driver = [s.strip() for s in row[0].text.split('.')]
            team = row[1].text
            results.append((None, driver, team, None))
        return results

    def weather(self):
        return self._soup.find('span', {'class': 'subInfo'}).text

    def points(self):
        table = self._soup.find_all('table', {'class': 'f1Table'})[2]
        results = []
        rows = table.find_all('tr', {'class': ['lineOne', 'lineTwo']})
        for row in rows:
            row = row.find_all('td')
            pos, _, driver = [s.strip() for s in row[1].text.split('.')]
            points = row[-1].text
            results.append((pos, driver, points))
        return results
