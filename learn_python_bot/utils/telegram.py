from telegram import ReplyMarkup, ParseMode
from telegram.error import BadRequest, Unauthorized

from learn_python_bot.api.telegram import get_bot
from learn_python_bot.config import TELEGRAM_BOT_TOKEN, TELEGRAM_PROXY_SETTINGS


def send_message(
    chat_id: str,
    message: str,
    reply_markup: ReplyMarkup = None,
    ignore_errors_on_send: bool = False,
    parse_markdown: bool = False,
) -> None:
    bot = get_bot(TELEGRAM_BOT_TOKEN, TELEGRAM_PROXY_SETTINGS)

    try:
        bot.send_message(
            chat_id,
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2 if parse_markdown else None,
        )
    except (BadRequest, Unauthorized):
        if not ignore_errors_on_send:
            raise
