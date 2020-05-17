import re
from typing import NamedTuple, Optional


class Student(NamedTuple):
    first_name: str
    last_name: str
    telegram_account: Optional[str]
    phone_number: Optional[str]
    knowledge_description: str
    purpose: Optional[str]
    airtable_id: str

    @property
    def is_telegram_account_valid(self) -> bool:
        min_account_length = 5
        telegram_account_regexp = r'^@[a-zA-Z0-9_]+$'
        if (
            self.telegram_account is None
            or len(self.telegram_account) < min_account_length
            or not re.match(telegram_account_regexp, self.telegram_account)
        ):
            return False
        return True
