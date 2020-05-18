from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from api.telegram import get_bot
from common_types import Student
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_PROXY_SETTINGS


def ask_for_feedback(student: Student, telegram_chat_id: str) -> None:
    bot = get_bot(TELEGRAM_BOT_TOKEN, TELEGRAM_PROXY_SETTINGS)
    bot.send_message(
        telegram_chat_id,
        text=f'Привет, {student.first_name}. Как тебе эта неделя?',
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton('👍', callback_data='w1_1'),
                InlineKeyboardButton('👎', callback_data='w1_2'),
            ]],
        ),
    )


if __name__ == '__main__':
    ask_for_feedback(
        student=Student(
            first_name='Илья',
            last_name='Лебедев',
            telegram_account='melevir',
            telegram_chat_id='123',
            phone_number='+79651111111',
            knowledge_description='',
            purpose=None,
            airtable_id='123',
        ),
        telegram_chat_id='187804971',
    )
