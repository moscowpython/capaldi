from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from click import command, option
from telegram.error import BadRequest

from api.airtable import AirtableAPI
from learn_python_bot.api.telegram import get_bot
from learn_python_bot.common_types import Student
from learn_python_bot.config import TELEGRAM_BOT_TOKEN, TELEGRAM_PROXY_SETTINGS


def ask_for_feedback(
    student: Student,
    week_num: int,
    ignore_errors_on_send: bool = False,
) -> None:
    bot = get_bot(TELEGRAM_BOT_TOKEN, TELEGRAM_PROXY_SETTINGS)
    reply_markup = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('👍', callback_data=f'w{week_num}_yay'),
            InlineKeyboardButton('👎', callback_data=f'w{week_num}_fuu'),
        ]],
    )
    try:
        bot.send_message(
            student.telegram_chat_id,
            text=f'Привет, {student.first_name}. Закончилась {week_num} неделя курса. Как она тебе?',
            reply_markup=reply_markup,
        )
    except BadRequest:
        if not ignore_errors_on_send:
            raise


@command()
@option('--debug', is_flag=True, default=False)
@option('--course_week_num', type=int, required=True)
def main(debug, course_week_num) -> None:
    if debug:
        students = [
            Student(
                first_name='Илья',
                last_name='Лебедев',
                telegram_account='melevir',
                telegram_chat_id='187804971',
                phone_number='+79651111111',
                knowledge_description='',
                purpose=None,
                airtable_id='123',
                airtable_pk=121,
            ),
        ]
    else:
        api = AirtableAPI.get_default_api()
        all_students = api.extract_students(
            api.fetch_students_data_from_airtable(),
        )
        students = [s for s in all_students if s.telegram_chat_id]
    for student in students:
        ask_for_feedback(student=student, week_num=course_week_num)


if __name__ == '__main__':
    main()
