import os
from logging import Logger

from requests import Session

from gservices import gspread_service


class Upload:

    def __init__(self, session: Session, logger: Logger):
        self.session = session
        self.logger = logger

    def upload(self, csv_filename):
        self.csv_filename = csv_filename
        self.logger.info(f"Uploading {self.csv_filename} to Google Sheet ...")
        data = self.data_from(self.csv_filename)
        self.clear_data_on_sheet()
        return gspread_service().spreadsheets().values().batchUpdate(
            spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
            body={
                'valueInputOption': 'USER_ENTERED',
                'data': data,
            },
        ).execute()

    def clear_data_on_sheet(self):
        return gspread_service().spreadsheets().values().batchClear(
            spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
            body={
                'ranges': self.cell_ranges(),
            },
        ).execute()

    def cell_ranges(self) -> list:
        pass

    def data_from(self, csv_filename) -> list:
        pass
