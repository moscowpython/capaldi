from telegram import Update
from telegram.ext import (
    CallbackContext, ConversationHandler, CommandHandler, MessageHandler,
    Filters,
)

from learn_python_bot.common_types import Student
from learn_python_bot.config import TELERGAM_ORGS_CHAT_ID
from learn_python_bot.decorators import for_students_only


# bot states
GETTING_FEEDBACK = 1


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
    context.bot_data['airtable_api'].save_feedback_on_demand(update.message.text, student)
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


def get_student_feedback_command_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler('feedback', feedback_command)],

        states={
            GETTING_FEEDBACK: [
                MessageHandler(Filters.text, handle_feedback),
            ],
        },
        fallbacks=[MessageHandler(Filters.text, something_went_wrong)],
    )
