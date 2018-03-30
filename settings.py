import os

base_dir = os.path.dirname(__file__)

STORAGE_PATH = os.path.abspath(os.path.join(base_dir, 'storage'))

# TODO: Вынести в .env файл
USE_PROXY = True

PROXY_CATALOG_PROTOCOL = 'https'
PROXY_CATALOG_DOMAIN = 'www.ip-adress.com'
