from gservices import gspread_service


def create_sheet(title):
    spreadsheet = {
        'properties': {
            'title': title
        },
    }
    return gspread_service().spreadsheets().create(
        body=spreadsheet
    ).execute()
