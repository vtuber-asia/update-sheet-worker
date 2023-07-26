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


if __name__ == '__main__':
    from dotenv import load_dotenv
    import os
    load_dotenv()
    created = create_sheet(os.getenv('GOOGLE_SHEET_TITLE'))
    print(f"Created sheet ID  : {created.get('spreadsheetId')}")
    print(f"Created sheet URL : {created.get('spreadsheetUrl')}")
