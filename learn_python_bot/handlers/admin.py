from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from learn_python_bot.decorators import for_admins_only


@for_admins_only
def admin_keyboard(update: Update, context: CallbackContext) -> None:
    keyboard = ReplyKeyboardMarkup([['Show students', 'Reload students', 'Restart bot']])
    update.message.reply_text('Hello admin', reply_markup=keyboard)


@for_admins_only
def admin_show_students(update: Update, context: CallbackContext) -> None:
    course_students: str = ''
    for student in context.dispatcher.bot_data['students']:
        course_students += f'{student.first_name} {student.last_name} {student.telegram_account}\n'

    update.message.reply_text(course_students)
