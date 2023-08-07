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
    copy_from_spreadsheet_id = '1O0E1IWeVZwV2W-6KwkAIBCbJ75ctMfyc4K4_VwpdhNQ'
    copy_from_ranges = 'K3:K'
    copy_to_spreadsheet_id = '1PfRJbdsNa9Kp4IfY6dNxAUulmGLBYKYpIq2M4j88v6M'
    copy_to_ranges = 'F3:F'
    values = fetch_cells_from(copy_from_spreadsheet_id, copy_from_ranges)
    write_cells_to(copy_to_spreadsheet_id, copy_to_ranges, values)
