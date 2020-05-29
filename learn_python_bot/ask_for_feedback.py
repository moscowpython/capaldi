from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from click import command, option

from learn_python_bot.api.airtable import AirtableAPI
from learn_python_bot.common_types import Student
from learn_python_bot.utils.telegram import send_message


def ask_for_feedback(
    student: Student,
    week_num: int,
    ignore_errors_on_send: bool = False,
) -> None:
    if not student.telegram_chat_id:
        return
    reply_markup = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('👍', callback_data=f'w{week_num}_yay'),
            InlineKeyboardButton('👎', callback_data=f'w{week_num}_fuu'),
        ]],
    )
    send_message(
        chat_id=student.telegram_chat_id,
        message=f'Привет, {student.first_name}. Закончилась {week_num} неделя курса. Как она тебе?',
        reply_markup=reply_markup,
        ignore_errors_on_send=ignore_errors_on_send,
    )


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
