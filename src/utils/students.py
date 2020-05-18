from typing import Optional, List

from common_types import Student


def get_student_by_tg_nickname(
    telegram_username: str,
    students: List[Student],
) -> Optional[Student]:
    matched_students = [
        s for s in students
        if s.telegram_account and s.telegram_account.strip('@') == telegram_username
    ]
    return matched_students[0] if matched_students else None
