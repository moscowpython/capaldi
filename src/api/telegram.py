from telegram import Bot
from telegram.utils.request import Request


def get_bot(telegram_bot_token, proxy_settings) -> Bot:
    return Bot(telegram_bot_token, request=Request(**proxy_settings))
