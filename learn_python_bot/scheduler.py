import datetime
import logging
from functools import partial

import pytz
import telegram
from prettytable import PrettyTable
from telegram.ext import Updater

from learn_python_bot.api.airtable import AirtableAPI
from learn_python_bot.bin.notify_on_tomorrow_event import main as notify_on_tomorrow
from learn_python_bot.bin.ask_for_feedback import ask_students_for_feedback
from learn_python_bot.bin.ask_curators_to_report import ask_curators_to_report
from learn_python_bot.bin.send_stat_report import send_report_to_orgs
from learn_python_bot.common_types import Event

logger = logging.getLogger(__name__)


def notify_on_tomorrow_job(context: telegram.ext.CallbackContext):
    logger.info('[SCHEDULER] starting regular check for next event notifications')
    notify_on_tomorrow()


def ask_students_for_feedback_job(week_num: int, context: telegram.ext.CallbackContext):
    logger.info('[SCHEDULER] starting students satisfaction feedback')
    ask_students_for_feedback(week_num)


def ask_curators_to_report_job(week_num: int, context: telegram.ext.CallbackContext):
    logger.info('[SCHEDULER] starting curators reports feedback')
    ask_curators_to_report(week_num)


def init_event_scheduler(updater: Updater, event: Event):
    now = datetime.datetime.now(pytz.timezone('Europe/Moscow'))

    day_before = event.offline_at - datetime.timedelta(hours=24)
    week_after = (event.offline_at + datetime.timedelta(days=7)).replace(hour=20)
    week_and_day_after = (event.offline_at + datetime.timedelta(days=8)).replace(hour=20)

    day_before_event_name = f'Day before notification: Week #{event.week_num}'
    satisfaction_feedback_event_name = f'Students satisfaction feedback: Week # {event.week_num}'
    curators_reports_event_name = f'Curators reports reminder: Week # {event.week_num}'
    orgs_reports_event_name = f'Orgs report: Week # {event.week_num}'

    if day_before > now:
        # Notification about tomorrows
        logger.info(f'[SCHEDULER] Planning day before notifications for '
                    f'event `{event.title}` at {day_before}')

        updater.job_queue.run_once(notify_on_tomorrow_job,
                                   day_before,
                                   name=day_before_event_name)

    if week_after > now:
        # Satisfaction feedback
        logger.info(f'[SCHEDULER] Planning satisactions request for '
                    f'event `{event.title}` at {week_after}')
        updater.job_queue.run_once(partial(ask_students_for_feedback_job, event.week_num),
                                   week_after,
                                   name=satisfaction_feedback_event_name)

        # Curators reminder
        logger.info(f'[SCHEDULER] Planning curators reports request for '
                    f'event `{event.title}` at {week_after}')
        updater.job_queue.run_once(partial(ask_curators_to_report_job, event.week_num),
                                   week_after,
                                   name=curators_reports_event_name)
    if week_and_day_after > now:
        # Orgs report
        logger.info(f'[SCHEDULER] Planning orgs report for'
                    f'event `{event.title}` at {week_and_day_after}')
        updater.job_queue.run_once(partial(send_report_to_orgs, event.week_num),
                                   week_and_day_after,
                                   name=orgs_reports_event_name)


def init_schedulers(updater: Updater):

    # Getting all events from calendar
    airtable_api = AirtableAPI.get_default_api()
    events = airtable_api.extract_events(
        airtable_api.fetch_events_data(),
    )

    events = sorted(events, key=lambda e: e.offline_at)

    for event in events:
        init_event_scheduler(updater, event)

    scheduler_table = PrettyTable()
    scheduler_table.field_names = ['Event', 'Datetime']

    for job in updater.job_queue.jobs():
        scheduler_table.add_row([job.name, job.next_t])

    logger.info(f'[SCHEDULER] Finish schedule preparation\n{scheduler_table}')
