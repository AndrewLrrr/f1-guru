from parsers.parser import Parser


class F1NewsTeamPointsParser(Parser):
    def points(self):
        table = self._soup.find('table', {'class': 'f1Table'})
        results = []
        rows = table.find_all('tr', {'class': ['lineOne', 'lineTwo']})
        for idx, row in enumerate(rows):
            row = row.find_all('td')
            try:
                pos, team = [s.strip() for s in row[0].text.split('.')]
            except ValueError:
                team = row[0].text.strip()
                pos = str(idx+1)
            points = row[-1].text
            results.append((pos, team, points))
        return results
