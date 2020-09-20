from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from learn_python_bot.decorators import for_admins_only


@for_admins_only
def admin_keyboard(update: Update, context: CallbackContext) -> None:
    keyboard = ReplyKeyboardMarkup([['Reload students']])
    update.message.reply_text('Hello admin', reply_markup=keyboard)
