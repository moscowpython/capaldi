import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from click import command, option, DateTime

from learn_python_bot.api.airtable import AirtableAPI
from learn_python_bot.utils.date import get_current_course_week
from learn_python_bot.utils.telegram import send_message


def ask_curators_to_report(course_week_num):
    reply_markup = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                'Начать',
                callback_data=f'curator_w{course_week_num}_start_report',
            ),
        ]],
    )

    airtable_api = AirtableAPI.get_default_api()
    students = airtable_api.extract_students(
        airtable_api.fetch_students_data(),
    )
    curators = airtable_api.fetch_curators()
    for curator in curators:
        group = [s for s in students if s.curator_id == curator.airtable_id]
        if not group or not curator.telegram_chat_id:
            continue
        send_message(
            chat_id=curator.telegram_chat_id,
            message=(
                f'Привет, {curator.name}. Закончилась {course_week_num} неделя курса. '
                f'Пора рассказать, как дела у твоих учеников.'
            ),
            reply_markup=reply_markup,
            ignore_errors_on_send=False,
        )


@command()
@option('--course_start_date', type=DateTime(), required=True)
def main(
    course_start_date: datetime.datetime,
) -> None:
    course_week_num = get_current_course_week(course_start_date.date())
    if not course_week_num:
        return

    ask_curators_to_report(course_week_num)


if __name__ == '__main__':
    main()
