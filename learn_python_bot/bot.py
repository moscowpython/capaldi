import logging
import os

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

from learn_python_bot.api.airtable import AirtableAPI
from learn_python_bot.utils.students import get_student_by_tg_nickname


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
            f'Кажется, ты не учишься на текущем наборе. Если это не так, то покажите '
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


def process_feedback(update: Update, context: CallbackContext) -> None:
    answers_map = {'yay': True, 'fuu': False}
    student = get_student_by_tg_nickname(update._effective_chat.username, STUDENTS)
    if student is None:
        update.message.reply_text(
            f'Кажется, ты не учишься на текущем наборе. Если это не так, то покажите '
            f'это сообщение кому-нибудь из администрации ({update._effective_chat.username})',
        )
        return None
    raw_response_text = update.callback_query.data
    week_num_str, raw_answer = raw_response_text.lstrip('w').split('_')
    week_num = int(week_num_str)
    if AIRTABLE_API.student_has_feedback_for_week(week_num, student.airtable_pk):
        response_text = f'Кажется, у нас уже есть твой фидбек за неделю {week_num}'
    else:
        AIRTABLE_API.save_feedback(student.airtable_id, week_num, answers_map[raw_answer])
        answer_text = 'понравилась' if answers_map[raw_answer] else 'не понравилась'
        response_text = f'Записал, что тебе {answer_text} неделя {week_num}. Спасибо за честность.'
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=response_text)


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
    dp.add_handler(CallbackQueryHandler(process_feedback))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
