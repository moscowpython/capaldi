import logging
import os
import sys
from threading import Thread

from telegram import Update
from telegram.ext import (
    Updater, CommandHandler, CallbackContext, CallbackQueryHandler,
    Filters, Dispatcher,
)
from sentry_sdk import init, capture_exception, configure_scope

from learn_python_bot import __version__
from learn_python_bot.config import (
    TELEGRAM_ADMIN_USERNAME, TELEGRAM_PROXY_SETTINGS, TELEGRAM_BOT_TOKEN,
)
from learn_python_bot.api.airtable import AirtableAPI
from learn_python_bot.handlers.start import start
from learn_python_bot.handlers.student_feedback_command import get_student_feedback_command_handler
from learn_python_bot.handlers.student_weekly_feedback import process_feedback


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)

init(os.environ['SENTRY_URL'], release=__version__)


def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    with configure_scope() as scope:
        scope.user = {
            'username': update._effective_chat.username,
            'chat_id': update._effective_chat.id,
        }
    capture_exception(
        context.error,
    )


def mutate_bot_to_be_restartable(updater: Updater):
    def stop_and_restart() -> None:
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    dp = updater.dispatcher
    dp.add_handler(CommandHandler(
        'restart',
        restart,
        filters=Filters.user(username=TELEGRAM_ADMIN_USERNAME),
    ))


def set_initial_bot_data(dispatcher: Dispatcher) -> None:
    airtable_api = AirtableAPI.get_default_api()
    students = airtable_api.extract_students(
        airtable_api.fetch_students_data_from_airtable(),
    )
    dispatcher.bot_data.update({
        'airtable_api': airtable_api,
        'students': students,
    })


def main() -> None:
    handlers = [
        CommandHandler('start', start),
        get_student_feedback_command_handler(),
        CallbackQueryHandler(process_feedback, pattern=r'w\w+_yay'),
    ]

    updater = Updater(
        TELEGRAM_BOT_TOKEN,
        use_context=True,
        request_kwargs=TELEGRAM_PROXY_SETTINGS,
    )
    dp = updater.dispatcher

    mutate_bot_to_be_restartable(updater)
    set_initial_bot_data(dp)
    for handler in handlers:
        dp.add_handler(handler)

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
