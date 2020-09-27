import logging
import os
import sys
from threading import Thread

from redis import Redis
from telegram import Update
from telegram.ext import (
    Updater, CommandHandler, CallbackContext, CallbackQueryHandler,
    Dispatcher, Filters, MessageHandler,
)
from sentry_sdk import init as init_setry, capture_exception, configure_scope

from learn_python_bot import __version__
from learn_python_bot.config import (TELEGRAM_PROXY_SETTINGS, TELEGRAM_BOT_TOKEN, REDIS_URL,
                                     SENTRY_URL)
from learn_python_bot.api.airtable import AirtableAPI
from learn_python_bot.decorators import for_admins_only
from learn_python_bot.handlers.admin import admin_keyboard, admin_show_students
from learn_python_bot.handlers.start import start
from learn_python_bot.handlers.student_feedback_command import get_student_feedback_command_handler
from learn_python_bot.handlers.student_weekly_feedback import process_feedback
from learn_python_bot.scheduler import init_schedulers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)

if SENTRY_URL:
    init_setry(SENTRY_URL, release=__version__)


def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    if SENTRY_URL:
        with configure_scope() as scope:
            scope.user = {
                'username': update._effective_chat.username,
                'chat_id': update._effective_chat.id,
            }
        capture_exception(
            context.error,
        )
    else:
        logger.error(context.error)


def mutate_bot_to_be_restartable(updater: Updater):
    def stop_and_restart() -> None:
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    @for_admins_only
    def restart(update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.regex('^(Restart bot)$'), restart))


def set_initial_bot_data(dispatcher: Dispatcher) -> None:
    airtable_api = AirtableAPI.get_default_api()
    students = airtable_api.extract_students(
        airtable_api.fetch_students_data(),
    )
    dispatcher.bot_data.update({
        'airtable_api': airtable_api,
        'students': students,
        'redis': Redis.from_url(REDIS_URL),
    })


@for_admins_only
def set_initial_bot_data_command(update: Update, context: CallbackContext) -> None:
    set_initial_bot_data(context.dispatcher)
    students_count = len(context.dispatcher.bot_data['students'])
    update.message.reply_text(f'Loaded {students_count} students')


def main() -> None:
    handlers = [
        CommandHandler('start', start),
        CommandHandler('admin', admin_keyboard),
        MessageHandler(Filters.regex('^(Show students)$'), admin_show_students),
        MessageHandler(Filters.regex('^(Reload students)$'), set_initial_bot_data_command),
        get_student_feedback_command_handler(),
        CallbackQueryHandler(process_feedback),
    ]

    updater = Updater(
        TELEGRAM_BOT_TOKEN,
        use_context=True,
        request_kwargs=TELEGRAM_PROXY_SETTINGS,
    )
    dp = updater.dispatcher

    mutate_bot_to_be_restartable(updater)
    init_schedulers(updater)
    set_initial_bot_data(dp)
    for handler in handlers:
        dp.add_handler(handler)

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
