import os


AIRTABLE_VIEW_NAME = 'Общая таблица'

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_PROXY_SETTINGS = {
    'proxy_url': os.environ['TELEGRAM_PROXY_URL'],
    'urllib3_proxy_kwargs': {
        'username': os.environ['TELEGRAM_PROXY_LOGIN'],
        'password': os.environ['TELEGRAM_PROXY_PASSWORD'],
    },
}
