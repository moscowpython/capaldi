import os


AIRTABLE_VIEW_NAME = 'Общая таблица'
AIRTABLE_RATE_LIMIT_STATUS_CODE = 429

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']

TELEGRAM_PROXY_SETTINGS = {}
if 'TELEGRAM_PROXY_URL' in os.environ:
    TELEGRAM_PROXY_SETTINGS = {
        'proxy_url': os.environ['TELEGRAM_PROXY_URL'],
        'urllib3_proxy_kwargs': {
            'username': os.environ['TELEGRAM_PROXY_LOGIN'],
            'password': os.environ['TELEGRAM_PROXY_PASSWORD'],
        },
    }
TELEGRAM_ADMIN_USERNAME = os.environ.get('TELEGRAM_ADMIN_USERNAME', '@melevir')
TELERGAM_ORGS_CHAT_ID = '-1001204501936'

REDIS_URL = os.environ.get('CAPALDI_REDIS_URL', 'redis://localhost:6379/0')
SENTRY_URL = os.environ.get('SENTRY_URL')
