from gservices import gspread_service
from dotenv import load_dotenv


def fetch_cells_from(spreadsheet_id: str, ranges: str) -> list:
    response = gspread_service().spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=ranges,
        valueRenderOption='FORMULA',
    ).execute()
    if 'values' in response:
        return response['values']
    return []


def write_cells_to(spreadsheet_id: str, ranges: str, values: list) -> None:
    return gspread_service().spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=ranges,
        valueInputOption='USER_ENTERED',
        body={
            'values': values
        }
    ).execute()


if __name__ == '__main__':
    load_dotenv()
    copy_from_spreadsheet_id = '' # TODO: fill this
    copy_from_ranges = '' # TODO: fill this
    copy_to_spreadsheet_id = '' # TODO: fill this
    copy_to_ranges = '' # TODO: fill this
    values = fetch_cells_from(copy_from_spreadsheet_id, copy_from_ranges)
    write_cells_to(copy_to_spreadsheet_id, copy_to_ranges, values)
