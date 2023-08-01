from gservices import gspread_service
from utils import cells_on_row
from links import remove_handler
from datetime import datetime
import requests
import os
import csv


def fetch_twitch_usernames_cells():
    return gspread_service().spreadsheets().values().get(
        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
        range="R3:R",
    ).execute()


def fetch_twitch_broadcast_ids_cells():
    return gspread_service().spreadsheets().values().get(
        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
        range="S3:S",
    ).execute()


def twitch_username_cells():
    response = fetch_twitch_usernames_cells()
    if 'values' in response:
        return list(map(cells_on_row, response['values']))
    return []


def rows_twitch_usernames_to_sheet_from(csv_filename):
    def to_text(username):
        if username is None or username == '':
            return username
        return f'=hyperlink("https://twitch.tv/{username}"; "@{username}")'
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        def map_row(row):
            return [to_text(row['username_twitch']) if 'username_twitch' in row else '']
        rows = list(map(map_row, reader))
        csvfile.close()
    for i, twitch_username_cell in enumerate(twitch_username_cells()):
        if twitch_username_cell is not None and rows[i] == '':
            rows[i] = to_text(remove_handler(twitch_username_cell))
    return rows
    

def fetch_twitch_usernames():
    values = fetch_twitch_usernames_cells()["values"]
    def filter_empty(row): return len(row) > 0
    def map_twitch_username(row): return row[0]
    return list(map(map_twitch_username, list(filter(filter_empty, values))))


def app_access_token():
    return requests.post(
        'https://id.twitch.tv/oauth2/token',
        params={
            'client_id': os.getenv('TWITCH_CLIENT_ID'),
            'client_secret': os.getenv('TWITCH_CLIENT_SECRET'),
            'grant_type': 'client_credentials'
        }
    ).json()['access_token']


def app_access_headers():
    return {
        'Authorization': f'Bearer {app_access_token()}',
        'Client-Id': os.getenv('TWITCH_CLIENT_ID')
    }


def fetch_users(usernames):
    return requests.get(
        'https://api.twitch.tv/helix/users',
        params={
            'login': usernames
        },
        headers=app_access_headers()
    ).json()


def fetch_followers_count_batch(broadcaster_ids, pool):
    result = pool.map(fetch_followers_count, broadcaster_ids)
    return result
    

def fetch_followers_count(broadcaster_id):
    print(f"Fetching followers count for {broadcaster_id}")
    response = requests.get(
        'https://api.twitch.tv/helix/channels/followers',
        params={
            'broadcaster_id': broadcaster_id
        },
        headers=app_access_headers()
    ).json()
    response['id'] = broadcaster_id
    return response


def find_twitch_channel(channels, twitch_login):
    for channel in channels:
        if channel["login"].lower() == remove_handler(twitch_login).lower():
            return channel
    return None


def find_followers_count(followers_counts, twitch_channel_id):
    for followers_count in followers_counts:
        if followers_count["id"] == twitch_channel_id:
            return followers_count
    return None


def store_twitch_channels(channels):
    twitch_channels_id_ranges = fetch_twitch_usernames_cells()["values"]
    write_rows = []
    for twitch_channel_id_rows in twitch_channels_id_ranges:
        if len(twitch_channel_id_rows) > 0:
            twitch_channel = find_twitch_channel(channels, twitch_channel_id_rows[0])
            if twitch_channel is not None:
                write_rows.append([
                    twitch_channel['id'],
                    cell_profile_image(twitch_channel),
                ])
            else:
                write_rows.append([
                    "",
                    ""
                ])
        else:
            write_rows.append([
                "",
                ""
            ])
    body = {
        "values": write_rows
    }
    return gspread_service().spreadsheets().values().update(
        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
        range="Q3:R",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


def store_followers_counts(followers_counts):
    twitch_channels_id_ranges = fetch_twitch_broadcast_ids_cells()["values"]
    write_rows = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for twitch_channel_id_rows in twitch_channels_id_ranges:
        if len(twitch_channel_id_rows) > 0:
            followers_count = find_followers_count(followers_counts, twitch_channel_id_rows[0])
            if followers_count is not None:
                write_rows.append([
                    followers_count['total'],
                    timestamp,
                ])
            else:
                write_rows.append([
                    "",
                    ""
                ])
        else:
            write_rows.append([
                "",
                ""
            ])
    body = {
        "values": write_rows
    }
    return gspread_service().spreadsheets().values().update(
        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
        range="S3:T",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


def cell_profile_image(twitch_channel):
    if 'profile_image_url' in twitch_channel \
            and twitch_channel['profile_image_url'] is not None:
        return f'=IMAGE("{twitch_channel["profile_image_url"]}"; 4; 80; 80)'
    else:
        return ""
