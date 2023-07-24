from auth import auth_google
from googleapiclient.discovery import build


def gspread_service():
    return build('sheets', 'v4', credentials=auth_google())


def gdrive_service():
    return build('drive', 'v3', credentials=auth_google())


def youtube_service():
    return build('youtube', 'v3', credentials=auth_google())
