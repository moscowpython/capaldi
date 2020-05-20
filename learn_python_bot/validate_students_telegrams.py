import os

from learn_python_bot.api.airtable import AirtableAPI
from learn_python_bot.config import AIRTABLE_VIEW_NAME


if __name__ == '__main__':
    api = AirtableAPI(
        airtable_api_token=os.environ['AIRTABLE_API_KEY'],
        airtable_base_id=os.environ['AIRTABLE_BASE_ID'],
        students_list_view_name=AIRTABLE_VIEW_NAME,
    )
    students = api.extract_students(api.fetch_students_data_from_airtable())

    for student in students:
        if not student.is_telegram_account_valid:
            print(  # noqa: T001
                f'{student.first_name} {student.last_name}: неправильная '
                f'ссылка на аккаунт в Telegram ({student.telegram_account})',
            )
