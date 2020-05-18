import os
from typing import List, Any, Mapping, NamedTuple

from requests import get, patch

from common_types import Student
from config import AIRTABLE_VIEW_NAME


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
        )

    def fetch_students_data_from_airtable(self) -> List[Mapping[str, Any]]:
        airtable_response = get(
            f'https://api.airtable.com/v0/{self.airtable_base_id}/current_course',
            params={'view': self.students_list_view_name},
            headers={'Authorization': f'Bearer {self.airtable_api_token}'},
        )
        raw_airtable_data = airtable_response.json() if airtable_response else None
        return raw_airtable_data.get('records', [])

    def extract_students(self, raw_students_data: List[Mapping[str, Any]]) -> List[Student]:
        return [self._extract_student_record(r) for r in raw_students_data]

    def set_telegram_chat_id(self, student_airtable_id: str, telegram_chat_id: int) -> Student:
        response = patch(
            f'https://api.airtable.com/v0/{self.airtable_base_id}/current_course',
            headers={'Authorization': f'Bearer {self.airtable_api_token}'},
            json={'records': [{'id': student_airtable_id, 'fields': {'chat_id': str(telegram_chat_id)}}]},
        ).json()
        return self._extract_student_record(response['records'][0])
