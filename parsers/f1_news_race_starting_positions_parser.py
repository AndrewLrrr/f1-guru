import re

from parsers.parser import Parser


class F1NewsRaceStartingPositionsParser(Parser):
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
                search_driver_with_pos = re.compile('^\d{1,2}\.\s*?[а-яА-Я.\s\-]{2,}$')
                search_driver = re.compile('^[а-яА-Я.\s\-]{2,}$')
                driver = None
                for s in content:
                    if search_driver_with_pos.search(s.text.strip()):
                        driver_info = [c.strip() for c in s.text.split('.') if c.strip()]
                        driver = [c.strip() for c in driver_info[1].split()][-1]
                    elif (
                        search_driver.search(s.text.strip())
                        and s.text.strip().lower() not in ('без времени', 'старт с пит-лейн',)
                    ):
                        driver = [c.strip() for c in s.text.split()][-1]
                pos = re.search('^(\d{1,2})\.?', item.text.strip(), re.MULTILINE)
                if pos:
                    pos = pos.group(1)
                time = re.search('(\d+:\d+\.\d+)', item.text.strip(), re.MULTILINE)
                if time:
                    time = time.group(1)
                if driver:
                    results.append((pos, driver, time))
        return results
