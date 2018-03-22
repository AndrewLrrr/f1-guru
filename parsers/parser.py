from bs4 import BeautifulSoup


class Parser:
    def __init__(self, data, parser='html.parser'):
        self._soup = BeautifulSoup(data, parser)
