from parsers.parser import Parser


class F1NewsTeamPointsParser(Parser):
    def points(self):
        table = self._soup.find('table', {'class': 'f1Table'})
        results = []
        rows = table.find_all('tr', {'class': ['lineOne', 'lineTwo']})
        for row in rows:
            row = row.find_all('td')
            pos, team = [s.strip() for s in row[0].text.split('.')]
            points = row[-1].text
            results.append((pos, team, points))
        return results
