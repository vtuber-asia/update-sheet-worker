from google.oauth2 import service_account
import os


def auth_google():
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets', 
        'https://www.googleapis.com/auth/youtube.readonly',
        'https://www.googleapis.com/auth/drive'
    ]
    SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_CREDENTIALS")
    credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return credentials
