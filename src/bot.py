import logging
import os

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from api.airtable import AirtableAPI
from utils.students import get_student_by_tg_nickname

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


AIRTABLE_API = AirtableAPI.get_default_api()
STUDENTS = AIRTABLE_API.extract_students(
    AIRTABLE_API.fetch_students_data_from_airtable(),
)


def start(update: Update, context: CallbackContext) -> None:
    student = get_student_by_tg_nickname(update._effective_chat.username, STUDENTS)
    if student is None:
        update.message.reply_text(
            f'Кажется, вы не учитесь на текущем наборе. Если это не так, то покажите '
            f'это сообщение кому-нибудь из администрации ({update._effective_chat.username})',
        )
        return None
    if student.telegram_chat_id:
        update.message.reply_text(
            f'Кажется, мы с вами уже знакомы. Привет, {student.first_name}.',
        )
        return None
    AIRTABLE_API.set_telegram_chat_id(student.airtable_id, update._effective_chat.id)
    update.message.reply_text(
        f'{student.first_name}, привет! Давай общаться. '
        f'Я буду иногда писать и спрашивать всякое.',
    )


def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main() -> None:
    proxy_settings = {
        'proxy_url': os.environ['TELEGRAM_PROXY_URL'],
        'urllib3_proxy_kwargs': {
            'username': os.environ['TELEGRAM_PROXY_LOGIN'],
            'password': os.environ['TELEGRAM_PROXY_PASSWORD'],
        },
    }
    updater = Updater(
        os.environ['TELEGRAM_BOT_TOKEN'],
        use_context=True,
        request_kwargs=proxy_settings,
    )

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
