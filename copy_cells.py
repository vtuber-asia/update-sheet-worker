from gservices import gspread_service
from inquirer import List, Text, prompt
from os import getenv


def fetch_cells_from(spreadsheet_id: str, ranges: str, output_opt: str) -> list:
    response = gspread_service().spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=ranges,
        valueRenderOption=output_opt,
    ).execute()
    if 'values' in response:
        return response['values']
    return []


def clear_cells_on(spreadsheet_id: str, ranges: str) -> None:
    return gspread_service().spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=ranges
    ).execute()


def write_cells_to(spreadsheet_id: str, ranges: str, input_opt: str, values: list) -> None:
    return gspread_service().spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=ranges,
        valueInputOption=input_opt,
        body={
            'values': values
        }
    ).execute()


def from_prompt() -> dict[str: str]:
    questions = [
        Text(
            'source_spreadsheet_id',
            message='Source Spreadsheet ID '
        ),
        Text(
            'source_range',
            message='Source Range '
        ),
        List(
            'source_value_render_option',
            message='How values should be rendered in the output?',
            choices=[
                'FORMULA',
                'FORMATTED_VALUE',
                'UNFORMATTED_VALUE',
            ],
            carousel=True
        ),
        Text(
            'dest_spreadsheet_id',
            message='Target Spreadsheet ID '
        ),
        Text(
            'dest_range',
            message='Target Range '
        ),
        List(
            'dest_value_render_option',
            message='How input data should be interpreted?',
            choices=[
                'USER_ENTERED',
                'RAW',
            ],
            carousel=True
        ),
    ]
    return prompt(questions)


def from_env() -> dict[str: str]:
    return {
        'dest_spreadsheet_id': getenv('DEST_SPREADSHEET_ID'),
        'dest_range': getenv('DEST_RANGE'),
        'dest_value_render_option': getenv('DEST_VALUE_RENDER_OPTION'),
        'source_spreadsheet_id': getenv('SOURCE_SPREADSHEET_ID'),
        'source_range': getenv('SOURCE_RANGE'),
        'source_value_render_option': getenv('SOURCE_VALUE_RENDER_OPTION')
    }


if __name__ == '__main__':
    answers: dict[str: str] = {}
    if getenv('USING_ENVIRONMENT') is None:
        answers = from_prompt()
    else:
        answers = from_env()
    print(
        write_cells_to(
            answers['dest_spreadsheet_id'],
            answers['dest_range'],
            answers['dest_value_render_option'],
            fetch_cells_from(
                answers['source_spreadsheet_id'],
                answers['source_range'],
                answers['source_value_render_option'],
            )
        )
    )
