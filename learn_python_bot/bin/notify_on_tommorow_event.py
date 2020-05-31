import datetime

from learn_python_bot.api.airtable import AirtableAPI
from learn_python_bot.common_types import Event
from learn_python_bot.utils.telegram import send_message


def create_message_for_tommorow_event(tommorow_event: Event) -> str:
    message = f'Завтра в {tommorow_event.at.hour}:{tommorow_event.at.minute} будет очередной созвон курса Learn Python.'
    if tommorow_event.zoom_url:
        message += f'\nВот ссылка на Зум: {tommorow_event.zoom_url}'
    return message


def main() -> None:
    airtable_api = AirtableAPI.get_default_api()
    students = airtable_api.extract_students(
        airtable_api.fetch_students_data_from_airtable(),
    )
    events = airtable_api.extract_events(
        airtable_api.fetch_events_data_from_airtable(),
    )

    tommorow = datetime.date.today() + datetime.timedelta(days=1)
    tommorow_events = [e for e in events if e.at.date() == tommorow]
    tommorow_event = tommorow_events[0] if tommorow_events else None

    if not tommorow_event:
        return

    message = create_message_for_tommorow_event(tommorow_event)

    for student in students:
        if not student.telegram_chat_id:
            continue
        send_message(
            chat_id=student.telegram_chat_id,
            message=message,
            ignore_errors_on_send=True,
        )


if __name__ == '__main__':
    main()
