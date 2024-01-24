from gservices import gspread_service
from inquirer import List, Text, prompt

def fetch_cells_from(spreadsheet_id: str, ranges: str, output_opt: str) -> list:
    response = gspread_service().spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=ranges,
        valueRenderOption=output_opt,
    ).execute()
    if 'values' in response:
        return response['values']
    return []


def write_cells_to(spreadsheet_id: str, ranges: str, input_opt: str, values: list) -> None:
    return gspread_service().spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=ranges,
        valueInputOption=input_opt,
        body={
            'values': values
        }
    ).execute()


if __name__ == '__main__':
    questions = [
        Text('source_spreadsheet_id', 
             message='Source Spreadsheet ID '),
        Text('source_range', 
             message='Source Range '),
        List('source_value_render_option', 
             message='How values should be rendered in the output?',
             choices=[
                 'FORMULA',
                 'FORMATTED_VALUE',
                 'UNFORMATTED_VALUE',
             ], 
             carousel=True
        ),
        Text('dest_spreadsheet_id', 
             message='Target Spreadsheet ID '),
        Text('dest_range', 
             message='Target Range '),
        List('dest_value_render_option', 
             message='How input data should be interpreted?',
             choices=[
                 'USER_ENTERED',
                 'RAW',
             ],
             carousel=True
        ),
    ]
    answers = prompt(questions)
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
