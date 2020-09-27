from typing import Optional, List

from learn_python_bot.common_types import Student


def get_student_by_tg_nickname(
    telegram_username: str,
    students: List[Student],
) -> Optional[Student]:
    matched_students = [
        s for s in students
        if s.telegram_account and names_equal(s.telegram_account, telegram_username)
    ]
    return matched_students[0] if matched_students else None


def names_equal(telegram_account: str, telegram_username: str) -> bool:
    return telegram_account.strip('@').lower() == telegram_username.lower()
