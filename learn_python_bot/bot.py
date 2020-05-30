import logging
import os
import sys
from threading import Thread
from typing import Any, Callable

import wrapt
from telegram import Update
from telegram.ext import (
    Updater, CommandHandler, CallbackContext, CallbackQueryHandler,
    Filters, ConversationHandler, MessageHandler,
)

from learn_python_bot.common_types import Student
from learn_python_bot.config import (
    TELEGRAM_ADMIN_USERNAME, TELEGRAM_PROXY_SETTINGS, TELEGRAM_BOT_TOKEN,
    TELERGAM_ORGS_CHAT_ID,
)
from learn_python_bot.api.airtable import AirtableAPI
from learn_python_bot.typical_responses import not_a_student
from learn_python_bot.utils.students import get_student_by_tg_nickname


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)

GETTING_FEEDBACK = 1

AIRTABLE_API = AirtableAPI.get_default_api()
STUDENTS = AIRTABLE_API.extract_students(
    AIRTABLE_API.fetch_students_data_from_airtable(),
)


@wrapt.decorator
def for_students_only(wrapped: Callable, instance: Any, args: Any, kwargs: Any) -> Any:
    update = args[0]
    student = get_student_by_tg_nickname(update._effective_chat.username, STUDENTS)
    if student is None:
        update.message.reply_text(not_a_student(update))
        return None
    kwargs['student'] = student
    return wrapped(*args, **kwargs)


@for_students_only
def start(update: Update, context: CallbackContext, student: Student) -> None:
    if student.telegram_chat_id:
        update.message.reply_text(
            f'Кажется, мы с вами уже знакомы. Привет, {student.first_name}.',
        )
        return None
    new_student = AIRTABLE_API.set_telegram_chat_id(student.airtable_id, update._effective_chat.id)
    if new_student:
        STUDENTS.remove(student)
        STUDENTS.append(new_student)
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


@for_students_only
def feedback_command(update: Update, context: CallbackContext, student: Student) -> int:
    update.message.reply_text(
        (
            f'Напиши любой фидбек, жалобу или идею. То, что ты напишешь, '
            f'не увидит твой куратор, увидят только организаторы.'
        ),
    )
    return GETTING_FEEDBACK


@for_students_only
def handle_feedback(update: Update, context: CallbackContext, student: Student) -> None:
    AIRTABLE_API.save_feedback_on_demand(update.message.text, student)
    context.bot.send_message(
        TELERGAM_ORGS_CHAT_ID,
        (
            f'Студент {student.last_name} {student.first_name} оставил '
            f'обратную связь:\n\n{update.message.text}'
        ),
    )
    update.message.reply_text('Спасибо за обратную связь.')
    return ConversationHandler.END


def something_went_wrong(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        (
            'Что-то пошло не так. Попробуй воспользоваться /feedback '
            'ещё раз или напиши кому-то из администраторов.'
        ),
    )
    return ConversationHandler.END


def main() -> None:
    updater = Updater(
        TELEGRAM_BOT_TOKEN,
        use_context=True,
        request_kwargs=TELEGRAM_PROXY_SETTINGS,
    )

    def stop_and_restart() -> None:
        """Gracefully stop the Updater and replace the current process with a new one."""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))

    dp.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('feedback', feedback_command)],

            states={
                GETTING_FEEDBACK: [
                    MessageHandler(Filters.text, handle_feedback),
                ],
            },
            fallbacks=[MessageHandler(Filters.text, something_went_wrong)],
        ),
    )

    dp.add_handler(CommandHandler(
        'restart',
        restart,
        filters=Filters.user(username=TELEGRAM_ADMIN_USERNAME),
    ))
    dp.add_handler(CallbackQueryHandler(process_feedback))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
