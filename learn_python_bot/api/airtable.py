import os
from typing import List, Any, Mapping, NamedTuple, Optional

from requests import get, patch, post

from learn_python_bot.common_types import Student
from learn_python_bot.config import AIRTABLE_VIEW_NAME, AIRTABLE_RATE_LIMIT_STATUS_CODE


class AirtableAPI(NamedTuple):
    airtable_api_token: str
    airtable_base_id: str
    students_list_view_name: str

    @staticmethod
    def get_default_api() -> 'AirtableAPI':
        return AirtableAPI(
            airtable_api_token=os.environ['AIRTABLE_API_KEY'],
            airtable_base_id=os.environ['AIRTABLE_BASE_ID'],
            students_list_view_name=AIRTABLE_VIEW_NAME,
        )

    @staticmethod
    def _extract_student_record(raw_airtable_record: Mapping[str, Any]) -> Student:
        return Student(
            first_name=raw_airtable_record['fields']['first_name'],
            last_name=raw_airtable_record['fields']['last_name'],
            telegram_account=raw_airtable_record['fields'].get('telegram'),
            telegram_chat_id=raw_airtable_record['fields'].get('chat_id'),
            phone_number=raw_airtable_record['fields'].get('phone'),
            knowledge_description=raw_airtable_record['fields']['knowledge_description'],
            purpose=raw_airtable_record['fields'].get('purpose'),
            airtable_id=raw_airtable_record['id'],
            airtable_pk=raw_airtable_record['fields']['PK'],
        )

    def fetch_students_data_from_airtable(self) -> List[Mapping[str, Any]]:
        raw_airtable_data = self._make_airtable_request(
            'current_course',
            params={'view': self.students_list_view_name},
        )
        return raw_airtable_data.get('records', []) if raw_airtable_data else []

    def extract_students(self, raw_students_data: List[Mapping[str, Any]]) -> List[Student]:
        return [self._extract_student_record(r) for r in raw_students_data]

    def set_telegram_chat_id(self, student_airtable_id: str, telegram_chat_id: int) -> Optional[Student]:
        raw_airtable_data = self._make_airtable_request(
            'current_course',
            method='patch',
            json={'records': [{
                'id': student_airtable_id,
                'fields': {'chat_id': str(telegram_chat_id)},
            }]},
        )
        return (
            self._extract_student_record(raw_airtable_data['records'][0])
            if raw_airtable_data
            else None
        )

    def student_has_feedback_for_week(self, week_num, student_airtable_pk) -> bool:
        raw_airtable_data = self._make_airtable_request(
            'weekly_feedback',
            params={'filterByFormula': f'AND(student={student_airtable_pk},week_num={week_num})'},
        )

        return bool(raw_airtable_data['records']) if raw_airtable_data else False

    def save_feedback(self, student_airtable_id, week_num, is_liked) -> None:
        self._make_airtable_request(
            'weekly_feedback',
            method='post',
            json={'records': [
                {'fields': {
                    'student': [student_airtable_id],
                    'week_num': week_num,
                    'liked': is_liked,
                }},
            ]},
        )

    def fetch_feedback_for_week(self, course_week_num: int) -> List[Mapping[str, Any]]:
        raw_airtable_data = self._make_airtable_request(
            'weekly_feedback',
            params={'filterByFormula': f'week_num={course_week_num}'},
        )

        return raw_airtable_data['records'] if raw_airtable_data else []

    def _make_airtable_request(
        self,
        table_name,
        method='get',
        params=None,
        json=None,
        retries_number=5,
    ) -> Optional[Mapping[str, Any]]:
        methods_map = {f.__name__: f for f in [get, post, patch]}
        airtable_response = None
        for _ in range(retries_number):
            airtable_response = methods_map[method](  # type: ignore
                f'https://api.airtable.com/v0/{self.airtable_base_id}/{table_name}',
                params=params or {},
                headers={'Authorization': f'Bearer {self.airtable_api_token}'},
                json=json or None,
            )
            if airtable_response.status_code != AIRTABLE_RATE_LIMIT_STATUS_CODE:
                break
        return airtable_response.json() if airtable_response else None
