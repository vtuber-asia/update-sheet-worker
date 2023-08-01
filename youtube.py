from gservices import gspread_service, youtube_service
from datetime import datetime
from youtube_ext import youtube_channel_for
from utils import split
import logging
import os
import csv


def fetch_channel_ids_cells():
    return gspread_service().spreadsheets().values().get(
        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
        range="H3:H"
    ).execute()


def youtube_channel_username_cells():
    response = gspread_service().spreadsheets().values().get(
        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
        range="G3:G"
    ).execute()
    if 'values' in response:
        def map_channel_username(row): return row[0] if len(row) > 0 else None
        return list(map(map_channel_username, response['values']))
    return []


def fetch_channel_ids():
    values = fetch_channel_ids_cells()["values"]
    def map_channel_id(row): return row[0]
    return list(map(map_channel_id, values))


def fetch_channels(channel_ids):
    return youtube_service().channels().list(
        part="snippet,statistics,brandingSettings",
        id=",".join(channel_ids)
    ).execute()


def store_channels(channels):
    channel_ids_ranges = fetch_channel_ids_cells()["values"]
    write_rows = []
    for channel_id_rows in channel_ids_ranges:
        channel = find_channel(channels, channel_id_rows[0])
        if channel is not None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            write_rows.append([
                cell_customUrl(channel),
                channel_id_rows[0],
                cell_title(channel),
                cell_thumbnail(channel),
                cell_banner(channel),
                cell_videos_count(channel),
                cell_views_count(channel),
                cell_subscribers_count(channel),
                timestamp
            ])
        else:
            write_rows.append([
                "",
                channel_id_rows[0],
                "",
                "",
                "",
                "",
                "",
                "",
                timestamp
            ])
    body = {
        "values": write_rows
    }
    return gspread_service().spreadsheets().values().update(
        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
        range="G3:O",
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()


def update_youtube_channels():
    csv_filename = f'{datetime.now().strftime("%Y%m%d%H%M%S")}_youtube_channels.csv'
    fields = [
        'username', 
        'channel_id', 
        'channel_title', 
        'badges',
        'is_membership_active', 
        'profile_image_url', 
        'banner_image_url'
    ]
    with open(csv_filename, 'w', newline='', encoding='iso-8859-1') as csvfile:
        w = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for username_cell in youtube_channel_username_cells():
            if username_cell is not None:
                youtube_channel = youtube_channel_for(username_cell)
                w.writerow(youtube_channel)
            else:
                w.writerow({})
        csvfile.close()
    with open(csv_filename, 'r', newline='', encoding='iso-8859-1') as csvfile:
        from_csv_youtube_channels = list(csv.DictReader(csvfile))
        youtube_channel_ids = list(
            map(lambda row: row['channel_id'], list(
                    filter(lambda row: row is not None, from_csv_youtube_channels)
                )
            )
        )
        csvfile.close()
    youtube_channel_ids_chunks = split(youtube_channel_ids, 50)
    for youtube_channel_ids_chunk in youtube_channel_ids_chunks:
        from_api_youtube_channels = fetch_channels(youtube_channel_ids_chunk)
        for from_api_youtube_channel in from_api_youtube_channels['items']:
            for from_csv_youtube_channel in from_csv_youtube_channels:
                if from_api_youtube_channel['id'] == from_csv_youtube_channel['channel_id']:
                    from_csv_youtube_channel['profile_image_url'] = from_api_thumbnail(from_api_youtube_channel)
                    from_csv_youtube_channel['banner_image_url'] = from_api_banner(from_api_youtube_channel)
                    from_csv_youtube_channel['videos_count'] = from_api_videos_count(from_api_youtube_channel)
                    from_csv_youtube_channel['views_count'] = from_api_views_count(from_api_youtube_channel)
                    from_csv_youtube_channel['subscribers_count'] = from_api_subscribers_count(from_api_youtube_channel)
                    from_csv_youtube_channel['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    break
    fields.extend([
        'videos_count', 
        'views_count', 
        'subscribers_count',
        'timestamp'
    ])
    with open(csv_filename, 'w', newline='', encoding='iso-8859-1') as csvfile:
        w = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(from_csv_youtube_channels)
        csvfile.close()
    with open(f'sorted-{csv_filename}', 'w', newline='', encoding='iso-8859-1') as csvfile:
        w = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(
            sorted(list(
                filter(
                    lambda row: row is not None and 'subscribers_count' in row, 
                    from_csv_youtube_channels
                )
            ), key=lambda row: int(row['subscribers_count']), reverse=True)
        )
        csvfile.close()
    data = [
        {
            'range': "G3:Q",
            'values': rows_youtube_channels_to_sheet_from(csv_filename),
        },
        {
            'range': "YouTube!A3:K",
            'values': rows_youtube_channels_to_sheet_from(f'sorted-{csv_filename}'),
        }
    ]
    gspread_service().spreadsheets().values().batchClear(
        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
        body={
            'ranges': [
                "G3:Q",
                "YouTube!A3:K"
            ]
        }
    ).execute()
    return gspread_service().spreadsheets().values().batchUpdate(
        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
        body={
            'data': data,
            'valueInputOption': 'USER_ENTERED'
        },
    ).execute()


def rows_youtube_channels_to_sheet_from(csv_filename):
    def to_text(badge):
        if badge == '':
            return ''
        if badge == 'OFFICIAL_ARTIST_BADGE':
            return f'=image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Bootstrap_music-note.svg/240px-Bootstrap_music-note.svg.png"; 4; 24; 24)'
        if badge == 'CHECK_CIRCLE_THICK':
            return f'=image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/YT_Official_Verified_Checkmark_Circle.svg/52px-YT_Official_Verified_Checkmark_Circle.svg.png"; 4; 24; 24)'
        logging.warning(f"Unknown YouTube badge: {badge}")
        return '❓'
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        def map_row(row):
            badges = list(map(to_text, row['badges'].split('+')))
            return [
                f'=hyperlink("https://www.youtube.com/{row["username"]}"; "{row["username"]}")',
                row['channel_id'],
                row['channel_title'],
                badges[0] if len(badges) > 0 else '',
                f'=image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Yellow_Star_with_rounded_edges.svg/42px-Yellow_Star_with_rounded_edges.svg.png"; 4; 24; 24)' if row['is_membership_active'] == 'True' else '',
                f'=image("{row["profile_image_url"]}"; 4; 80; 80)',
                f'=image("{row["banner_image_url"]}"; 4; 73; 130)',
                row['videos_count'],
                row['views_count'],
                row['subscribers_count'],
                row['timestamp'],
            ]
        rows = list(map(map_row, reader))
        csvfile.close()
    return rows


def find_channel(channels, channel_id):
    for channel in channels:
        if channel["id"] == channel_id:
            return channel
    return None


def cell_customUrl(channel):
    if 'snippet' in channel \
            and 'customUrl' in channel['snippet']:
        return f'=hyperlink("https://www.youtube.com/{channel["snippet"]["customUrl"]}"; "{channel["snippet"]["customUrl"]}")'
    else:
        return ""


def cell_title(channel):
    if 'snippet' in channel \
            and 'title' in channel['snippet']:
        return channel['snippet']['title']
    else:
        return ""


def cell_thumbnail(channel):
    if 'snippet' in channel \
            and 'thumbnails' in channel['snippet'] \
            and 'default' in channel['snippet']['thumbnails'] \
            and 'url' in channel['snippet']['thumbnails']['default']:
        return f'=IMAGE("{channel["snippet"]["thumbnails"]["default"]["url"]}"; 4; 80; 80)'
    else:
        return ""


def cell_banner(channel):
    if 'brandingSettings' in channel \
            and 'image' in channel['brandingSettings'] \
            and 'bannerExternalUrl' in channel['brandingSettings']['image']:
        return f'=IMAGE("{channel["brandingSettings"]["image"]["bannerExternalUrl"]}"; 4; 73; 130)'
    else:
        return ""


def cell_videos_count(channel):
    if 'statistics' in channel \
            and 'videoCount' in channel['statistics']:
        return channel['statistics']['videoCount']
    else:
        return ""


def cell_views_count(channel):
    if 'statistics' in channel \
            and 'viewCount' in channel['statistics']:
        return channel['statistics']['viewCount']
    else:
        return ""


def cell_subscribers_count(channel):
    if 'statistics' in channel \
            and 'subscriberCount' in channel['statistics']:
        return channel['statistics']['subscriberCount']
    else:
        return ""


def from_api_thumbnail(from_api_youtube_channel):
    if 'snippet' in from_api_youtube_channel \
            and 'thumbnails' in from_api_youtube_channel['snippet'] \
            and 'default' in from_api_youtube_channel['snippet']['thumbnails'] \
            and 'url' in from_api_youtube_channel['snippet']['thumbnails']['default']:
        return from_api_youtube_channel['snippet']['thumbnails']['default']['url']
    else:
        return None
    

def from_api_banner(from_api_youtube_channel):
    if 'brandingSettings' in from_api_youtube_channel \
            and 'image' in from_api_youtube_channel['brandingSettings'] \
            and 'bannerExternalUrl' in from_api_youtube_channel['brandingSettings']['image']:
        return from_api_youtube_channel['brandingSettings']['image']['bannerExternalUrl']
    else:
        return None
    

def from_api_videos_count(from_api_youtube_channel):
    if 'statistics' in from_api_youtube_channel \
            and 'videoCount' in from_api_youtube_channel['statistics']:
        return from_api_youtube_channel['statistics']['videoCount']
    else:
        return None
    

def from_api_views_count(from_api_youtube_channel):
    if 'statistics' in from_api_youtube_channel \
            and 'viewCount' in from_api_youtube_channel['statistics']:
        return from_api_youtube_channel['statistics']['viewCount']
    else:
        return None
    

def from_api_subscribers_count(from_api_youtube_channel):
    if 'statistics' in from_api_youtube_channel \
            and 'subscriberCount' in from_api_youtube_channel['statistics']:
        return from_api_youtube_channel['statistics']['subscriberCount']
    else:
        return None
