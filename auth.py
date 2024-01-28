from google.oauth2 import service_account
from pathlib import Path
from os import getenv


def auth_google():
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/youtube.readonly',
        'https://www.googleapis.com/auth/drive'
    ]
    SERVICE_ACCOUNT_FILE = getenv('SERVICE_ACCOUNT_FILE')
    if not Path(SERVICE_ACCOUNT_FILE).is_file():
        raise ServiceAccountFileNotFound()
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return credentials


class ServiceAccountFileNotFound(Exception):
    pass
