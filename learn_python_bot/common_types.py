import datetime
import re
from typing import NamedTuple, Optional


class Student(NamedTuple):
    first_name: str
    last_name: str
    telegram_account: Optional[str]
    telegram_chat_id: Optional[str]
    phone_number: Optional[str]
    knowledge_description: str
    purpose: Optional[str]
    airtable_id: str
    airtable_pk: int
    curator_id: Optional[str]

    @property
    def name(self) -> str:
        return f'{self.last_name} {self.first_name}'

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


class Event(NamedTuple):
    title: str
    at: datetime.datetime
    zoom_url: Optional[str]


class Curator(NamedTuple):
    name: str
    telegram_account: Optional[str]
    telegram_chat_id: Optional[str]
    airtable_id: str
