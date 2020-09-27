import datetime
from typing import NamedTuple, Mapping, Any, List

from click import command, option, DateTime

from learn_python_bot.api.airtable import AirtableAPI
from learn_python_bot.config import TELERGAM_ORGS_CHAT_ID
from learn_python_bot.utils.date import get_current_course_week
from learn_python_bot.utils.telegram import send_message


class FeedbackStatistics(NamedTuple):
    week_num: int
    liked: int
    disliked: int

    @property
    def total(self) -> int:
        return self.liked + self.disliked

    @property
    def liked_percents(self) -> int:
        return int(self.liked / self.total * 100)


def fetch_feedback_data_from_api(course_week_num: int) -> FeedbackStatistics:
    api = AirtableAPI.get_default_api()
    raw_stat = api.fetch_feedback_for_week(course_week_num)
    return aggregate_feedback_data(raw_stat)


def aggregate_feedback_data(raw_stat: List[Mapping[str, Any]]) -> FeedbackStatistics:
    week_num = raw_stat[0]['fields']['week_num']
    liked = sum(1 for r in raw_stat if r['fields'].get('score') == 1)
    disliked = len(raw_stat) - liked
    return FeedbackStatistics(week_num=week_num, liked=liked, disliked=disliked)


def create_report(report_data: FeedbackStatistics) -> str:
    return (
        f'Статистика по фидбеку за {report_data.week_num}-ю неделю. '
        f'Пофидбечили {report_data.total} студентов, лайк поставили {report_data.liked} '
        f'({report_data.liked_percents}%).'
    )


def send_report_to_orgs(course_week_num: int) -> None:
    report_data = fetch_feedback_data_from_api(course_week_num)
    report_str = create_report(report_data)

    send_message(TELERGAM_ORGS_CHAT_ID, message=report_str, ignore_errors_on_send=True)


@command()
@option('--course_week_num', type=int)
@option('--course_start_date', type=DateTime())
def main(course_week_num: int = None, course_start_date: datetime.datetime = None) -> None:
    if not course_week_num and course_start_date:
        course_week_num = get_current_course_week(course_start_date.date())
    if course_week_num:
        send_report_to_orgs(course_week_num)


if __name__ == '__main__':
    main()
