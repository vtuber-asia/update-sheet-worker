from gservices import gspread_service, youtube_service
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup


def fetch_channel_ids_cells():
    return gspread_service().spreadsheets().values().get(
        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
        range="H3:H"
    ).execute()


def fetch_channel_ids():
    values = fetch_channel_ids_cells()["values"]
    map_channel_id = lambda row: row[0]
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
                cell_link(channel),
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
                "",
                timestamp
            ])
    body = {
        "values": write_rows
    }
    return gspread_service().spreadsheets().values().update(
        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
        range="G3:P",
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()


def find_channel(channels, channel_id):
    for channel in channels:
        if channel["id"] == channel_id:
            return channel
    return None


def cell_customUrl(channel):
    if 'snippet' in channel \
            and 'customUrl' in channel['snippet']:
        return channel['snippet']['customUrl']
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
        return '=IMAGE("{}"; 4; 80; 80)'.format(channel["snippet"]["thumbnails"]["default"]["url"])
    else:
        return ""


def cell_banner(channel):
    if 'brandingSettings' in channel \
            and 'image' in channel['brandingSettings'] \
            and 'bannerExternalUrl' in channel['brandingSettings']['image']:
        return '=IMAGE("{}"; 4; 73; 130)'.format(channel["brandingSettings"]["image"]["bannerExternalUrl"])
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
    

def cell_link(channel):
    if 'id' in channel:
        return '=hyperlink("https://www.youtube.com/channel/{}"; "LINK")'.format(channel["id"])
    else:
        return ""
