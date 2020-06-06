import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from click import command, option, DateTime

from learn_python_bot.api.airtable import AirtableAPI
from learn_python_bot.common_types import Student
from learn_python_bot.utils.date import get_current_course_week
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
@option('--course_week_num', type=int)
@option('--course_start_date', type=DateTime())
def main(
    course_week_num: int = None,
    course_start_date: datetime.datetime = None,
) -> None:
    if not course_week_num and course_start_date:
        course_week_num = get_current_course_week(course_start_date.date())
    if not course_week_num:
        return

    api = AirtableAPI.get_default_api()
    all_students = api.extract_students(
        api.fetch_students_data_from_airtable(),
    )
    students = [s for s in all_students if s.telegram_chat_id]
    for student in students:
        ask_for_feedback(student=student, week_num=course_week_num)


if __name__ == '__main__':
    main()
