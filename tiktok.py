from gservices import gspread_service
import os
from datetime import datetime


def fetch_tiktok_usernames_cells():
    return gspread_service().spreadsheets().values().get(
        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
        range="U3:U"
    ).execute()


def fetch_tiktok_usernames():
    values = fetch_tiktok_usernames_cells()["values"]
    def filter_empty(row): return len(row) > 0
    def map_tiktok_username(row): return row[0]
    return list(map(map_tiktok_username, list(filter(filter_empty, values))))


def find_tiktok_channel(tiktok_channels, tiktok_username):
    for tiktok_channel in tiktok_channels:
        if tiktok_channel["username"] == tiktok_username:
            return tiktok_channel
    return None


def store_tiktok_channels(tiktok_channels):
    tiktok_channels_ranges = fetch_tiktok_usernames_cells()["values"]
    write_rows = []
    for tiktok_channel_rows in tiktok_channels_ranges:
        if len(tiktok_channel_rows) > 0:
            tiktok_channel = find_tiktok_channel(tiktok_channels, tiktok_channel_rows[0])
            if tiktok_channel is not None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                write_rows.append([
                    tiktok_channel['id'],
                    cell_thumbnail(tiktok_channel),
                    cell_followers_count(tiktok_channel),
                    cell_hearts_count(tiktok_channel),
                    cell_videos_count(tiktok_channel),
                    timestamp
                ])
            else:
                write_rows.append([
                    "",
                    "",
                    "",
                    "",
                    "",
                    ""
                ])
        else:
            write_rows.append([
                "",
                "",
                "",
                "",
                "",
                ""
            ])
    body = {
        "values": write_rows
    }
    return gspread_service().spreadsheets().values().update(
        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
        range="V3:AA",
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()


def cell_thumbnail(tiktok_channel):
    if 'thumbnail' in tiktok_channel and tiktok_channel['thumbnail'] is not None:
        return f'=image("{tiktok_channel["thumbnail"]}"; 4; 80; 80)'
    else:
        return ""
    

def cell_followers_count(tiktok_channel):
    if 'followers_count' in tiktok_channel and tiktok_channel['followers_count'] is not None:
        return tiktok_channel['followers_count']
    else:
        return 0
    

def cell_hearts_count(tiktok_channel):
    if 'hearts_count' in tiktok_channel and tiktok_channel['hearts_count'] is not None:
        return tiktok_channel['hearts_count']
    else:
        return 0
    

def cell_videos_count(tiktok_channel):
    if 'videos_count' in tiktok_channel and tiktok_channel['videos_count'] is not None:
        return tiktok_channel['videos_count']
    else:
        return 0


if __name__ == '__main__':
    from dotenv import load_dotenv
    from utils import split
    from tiktok_ext import fetch_tiktok_channels
    import time

    load_dotenv()
    tiktok_username_slices = split(fetch_tiktok_usernames(), 50)
    tiktok_channels = []
    for slice in tiktok_username_slices:
        fetched = fetch_tiktok_channels(slice)
        tiktok_channels.extend(fetched)
        time.sleep(1)
    print(store_tiktok_channels(tiktok_channels))
