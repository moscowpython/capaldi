from telegram import Update
from telegram.ext import CallbackContext

from learn_python_bot.common_types import Student
from learn_python_bot.decorators import for_students_only


@for_students_only
def start(update: Update, context: CallbackContext, student: Student) -> None:
    if student.telegram_chat_id:
        update.message.reply_text(
            f'Кажется, мы с вами уже знакомы. Привет, {student.first_name}.',
        )
        return None
    new_student = context.bot_data['airtable_api'].set_telegram_chat_id(
        student.airtable_id,
        update._effective_chat.id,
    )
    if new_student:
        context.bot_data['students'].remove(student)
        context.bot_data['students'].append(new_student)
    update.message.reply_text(
        f'{student.first_name}, привет! Давай общаться. '
        f'Я буду иногда писать и спрашивать всякое.',
    )
