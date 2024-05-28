from os import getenv
from logging import Logger

from requests import Session

from gservices import gspread_service


class Upload:

    def __init__(self, csv_filename: str, session: Session, logger: Logger):
        self.csv_filename = csv_filename
        self.session = session
        self.logger = logger

    def upload(self):
        self.logger.info(f"Uploading {self.csv_filename} to Google Sheet ...")
        data = self.data_from()
        if self.is_empty_data(data):
            raise TryingToUploadEmptySheet(f"Data on {self.csv_filename} is empty, upload canceled.")
        self.clear_data_on_sheet()
        return [
            gspread_service().spreadsheets().values().batchUpdate(
                spreadsheetId=getenv("GOOGLE_SHEET_ID_SRC"),
                body={
                    'valueInputOption': 'USER_ENTERED',
                    'data': [data[0]],
                },
            ).execute(),
            gspread_service().spreadsheets().values().batchUpdate(
                spreadsheetId=getenv("GOOGLE_SHEET_ID_DEST"),
                body={
                    'valueInputOption': 'USER_ENTERED',
                    'data': [data[1]],
                },
            ).execute()
        ]

    def clear_data_on_sheet(self):
        return gspread_service().spreadsheets().values().batchClear(
            spreadsheetId=getenv("GOOGLE_SHEET_ID_DEST"),
            body={
                'ranges': self.cell_ranges(),
            },
        ).execute()

    def cell_ranges(self) -> list:
        return [
            getenv('GOOGLE_SHEET_RANGE_DEST'),
        ]

    def data_from(self) -> list:
        pass

    def is_empty_data(self, data: list) -> bool:
        return len([item for item in data[0]['values'][0] if item == '']) == len(data[0]['values'][0]) \
            and len([item for item in data[0]['values'] if item == data[0]['values'][0]]) == len(data[0]['values'])


class TryingToUploadEmptySheet(Exception):
    pass
