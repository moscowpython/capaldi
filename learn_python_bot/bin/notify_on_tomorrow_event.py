import datetime
import logging

from learn_python_bot.api.airtable import AirtableAPI
from learn_python_bot.common_types import Event
from learn_python_bot.utils.telegram import send_message

logger = logging.getLogger(__name__)


def timedelta_hours(delta: datetime.timedelta):
    return int((delta.days * 24 * 3600 + delta.seconds) / 3600)


def create_online_message_for_tomorrow_event(event: Event) -> str:
    message = (f'Завтра в {event.online_at.hour}:{event.online_at.minute} будет'
               f' очередной созвон курса Learn Python.')

    if event.zoom_url:
        message += f'\nВот ссылка на Зум: {event.zoom_url}'
    return message


def create_offline_message_for_tomorrow_event(event: Event) -> str:
    message = (f'Завтра в {event.offline_at.hour}:{event.offline_at.minute} будет '
               f'очередное занятие курса Learn Python.')

    if event.where:
        message += f'\nЗанятие пройдет в {event.where}'
    return message


def main() -> None:
    airtable_api = AirtableAPI.get_default_api()
    students = airtable_api.extract_students(
        airtable_api.fetch_students_data(),
    )
    events = airtable_api.extract_events(
        airtable_api.fetch_events_data(),
    )

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_events = [e for e in events if e.online_at.date() == tomorrow]
    tomorrow_event = tomorrow_events[0] if tomorrow_events else None
    if not tomorrow_event:
        logger.info('No pending events yet')
        return

    logger.info('Time to notify students about event tomorrow')
    online_message = create_online_message_for_tomorrow_event(tomorrow_event)
    offline_message = create_offline_message_for_tomorrow_event(tomorrow_event)

    for student in students:
        if not student.telegram_chat_id:
            continue
        send_message(
            chat_id=student.telegram_chat_id,
            message=online_message if student.is_online() else offline_message,
            ignore_errors_on_send=True,
        )


if __name__ == '__main__':
    main()
