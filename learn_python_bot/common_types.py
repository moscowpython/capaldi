import datetime
import re
from typing import NamedTuple, Optional

STUDENT_TYPE_ONLINE = 'онлайн'
STUDENT_TYPE_OFFLINE = 'оффлайн'


class Student(NamedTuple):
    first_name: str
    last_name: str
    group_type: str
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

    def is_online(self) -> bool:
        return self.group_type == STUDENT_TYPE_ONLINE

    def is_offline(self) -> bool:
        return self.group_type == STUDENT_TYPE_OFFLINE


class Event(NamedTuple):
    title: str
    online_at: datetime.datetime
    offline_at: datetime.datetime
    zoom_url: Optional[str]
    where: Optional[str]

    @property
    def week_num(self) -> str:
        return self.title.split()[0]


class Curator(NamedTuple):
    name: str
    telegram_account: Optional[str]
    telegram_chat_id: Optional[str]
    airtable_id: str
