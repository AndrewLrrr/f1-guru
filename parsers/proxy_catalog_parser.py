from parsers.parser import Parser


class ProxyCatalogParser(Parser):
    def proxy_ips(self):
        ips = []

        objects_list = self._soup.find('table', {'class': 'proxylist'})

        for tr in objects_list.find('tbody').find_all('tr'):
            item = tr.find_all('td')[0]
            ips.append(item.text)

        return ips
