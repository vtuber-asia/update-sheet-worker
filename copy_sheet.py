from gservices import gspread_service
from inquirer import Text, prompt


def copy_sheet_from(spreadsheet_id: str, sheet_id: str, copy_to_spreadsheet_id: str):
    return gspread_service().spreadsheets().sheets().copyTo(
        spreadsheetId=spreadsheet_id,
        sheetId=sheet_id,
        body={
            'destinationSpreadsheetId': copy_to_spreadsheet_id
        }
    ).execute()


if __name__ == '__main__':
    questions = [
        Text(
            'spreadsheet_id',
            message='Source Spreadsheet ID '
        ),
        Text(
            'sheet_id',
            message='Sheet ID              '
        ),
        Text(
            'copy_to_spreadsheet_id',
            message='Target Spreadsheet ID '
        ),
    ]
    answers = prompt(questions)
    spreadsheet_id = answers['spreadsheet_id']
    sheet_id = answers['sheet_id']
    target_spreadsheet_id = answers['copy_to_spreadsheet_id']
    print(
        copy_sheet_from(
            spreadsheet_id=spreadsheet_id,
            sheet_id=sheet_id,
            copy_to_spreadsheet_id=target_spreadsheet_id,
        )
    )
