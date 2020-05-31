from learn_python_bot.api.airtable import AirtableAPI


def main() -> None:
    airtable_api = AirtableAPI.get_default_api()
    students = airtable_api.extract_students(
        airtable_api.fetch_students_data_from_airtable(),
    )
    curators = airtable_api.fetch_curators()
    for curator in curators:
        group = [s for s in students if s.curator_id == curator.airtable_id]
        if not group:
            continue
        print(curator.name)  # noqa: T001
        for student in group:
            print('\t', student.name)  # noqa: T001


if __name__ == '__main__':
    main()
