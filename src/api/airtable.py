from typing import List, Any, Mapping, NamedTuple

from requests import get

from common_types import Student


class AirtableAPI(NamedTuple):
    airtable_api_token: str
    airtable_base_id: str
    students_list_view_name: str

    def fetch_students_data_from_airtable(self) -> List[Mapping[str, Any]]:
        airtable_response = get(
            f'https://api.airtable.com/v0/{self.airtable_base_id}/current_course',
            params={'view': self.students_list_view_name},
            headers={'Authorization': f'Bearer {self.airtable_api_token}'},
        )
        raw_airtable_data = airtable_response.json() if airtable_response else None
        return raw_airtable_data.get('records', [])

    def extract_students(self, raw_students_data: List[Mapping[str, Any]]) -> List[Student]:
        students: List[Student] = []
        for raw_student in raw_students_data:
            students.append(Student(
                first_name=raw_student['fields']['first_name'],
                last_name=raw_student['fields']['last_name'],
                telegram_account=raw_student['fields'].get('telegram'),
                phone_number=raw_student['fields'].get('phone'),
                knowledge_description=raw_student['fields']['knowledge_description'],
                purpose=raw_student['fields'].get('purpose'),
                airtable_id=raw_student['id'],
            ))
        return students
