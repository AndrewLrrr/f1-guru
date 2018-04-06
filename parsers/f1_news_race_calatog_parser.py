from parsers.parser import Parser


class F1NewsRaceCatalogParser(Parser):
    def links(self):
        table = self._soup.find('table', {'class': 'f1Table'})
        results = []
        rows = table.find_all('tr', {'class': ['lineOne', 'lineTwo']})
        for row in rows:
            row = row.find_all('td')
            link = row[2].find('a', href=True)
            if link:
                results.append(row[2].find('a', href=True)['href'])
        return tuple(results)

    def tracks(self):
        table = self._soup.find('table', {'class': 'f1Table'})
        results = []
        rows = table.find_all('tr', {'class': ['lineOne', 'lineTwo']})
        for row in rows:
            row = row.find_all('td')
            results.append(row[3].text)
        return tuple(results)

    def laps(self):
        table = self._soup.find('table', {'class': 'f1Table'})
        results = []
        rows = table.find_all('tr', {'class': ['lineOne', 'lineTwo']})
        for row in rows:
            row = row.find_all('td')
            results.append(row[5].text.replace('*', ''))
        return tuple(results)
