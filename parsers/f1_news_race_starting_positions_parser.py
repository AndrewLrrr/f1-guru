import re

from parsers.parser import Parser


class F1NewsRaceStartingPositionsParser(Parser):
    def __init__(self, data):
        super().__init__(data)
        self._search_driver_with_pos = re.compile('^\d{1,2}\.\s*?[а-яА-Я.\s\-]{2,}$')
        self._search_driver = re.compile('^[а-яА-Я.\s\-]{2,}$')
        self._fix_extra_spaces = re.compile('\s{2,}')

    def positions(self):
        table = self._soup.find('div', {'id': 'content'}).find('table')
        rows = table.find_all('tr')
        results = []
        for row in rows:
            data = row.find_all('td')
            for item in data:
                if not item.text.strip():
                    continue
                content = item.find_all('b')
                if not content:
                    continue
                driver = None
                for s in content:
                    driver = self._driver_searcher(s.text)
                    if driver:
                        break
                pos = re.search('^(\d{1,2})\.?', item.text.strip(), re.MULTILINE)
                if pos:
                    pos = pos.group(1)
                time = re.search('(\d+:\d+\.\d+)', item.text.strip(), re.MULTILINE)
                if time:
                    time = time.group(1)
                if driver:
                    results.append((pos, driver, time))
        return results

    def _driver_searcher(self, text):
        driver = None
        if self._search_driver_with_pos.search(text.strip()):
            driver_info = [c.strip().strip('.') for c in text.split('.') if c.strip()]
            driver = [c.strip() for c in driver_info[1].split()][-1]
            if driver.find('-') != -1:
                driver = driver.split('-')[0]
        elif (
            self._search_driver.search(text.strip())
            and self._fix_extra_spaces.sub(' ', text).strip().lower() not in ('без времени', 'старт с пит-лейн',)
        ):
            driver = [c.strip() for c in text.split()][-1]
            if driver.find('-') != -1:
                driver = driver.split('-')[0]
        return driver
