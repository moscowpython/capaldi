import os
from pprint import pprint
from typing import List, Any, Mapping

from requests import get

from config import AIRTABLE_VIEW_NAME


def fetch_students_data_from_airtable(
    airtable_base_id: str,
    airtable_api_token: str,
    airtable_view_name: str,
) -> List[Mapping[str, Any]]:
    airtable_response = get(
        f'https://api.airtable.com/v0/{airtable_base_id}/current_course',
        params={'view': airtable_view_name},
        headers={'Authorization': f'Bearer {airtable_api_token}'},
    )
    raw_airtable_data = airtable_response.json() if airtable_response else None
    return raw_airtable_data.get('records', [])


if __name__ == '__main__':
    pprint(
        fetch_students_data_from_airtable(
            airtable_base_id=os.environ.get('AIRTABLE_BASE_ID'),
            airtable_api_token=os.environ.get('AIRTABLE_API_KEY'),
            airtable_view_name=AIRTABLE_VIEW_NAME,
        )
    )
