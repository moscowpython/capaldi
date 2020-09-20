from learn_python_bot.api.airtable import AirtableAPI


if __name__ == '__main__':
    api = AirtableAPI.get_default_api()
    students = api.extract_students(api.fetch_students_data())

    for student in students:
        if not student.is_telegram_account_valid:
            print(  # noqa: T001
                f'{student.first_name} {student.last_name}: неправильная '
                f'ссылка на аккаунт в Telegram ({student.telegram_account})',
            )
