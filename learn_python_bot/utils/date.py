import datetime


def get_current_course_week(course_start_date: datetime.date) -> int:
    return (datetime.date.today() - course_start_date).days // 7
