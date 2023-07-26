from dotenv import load_dotenv
from youtube import fetch_channel_ids, fetch_channel_ids_cells
from youtube_ext import fetch_channel_depths
from utils import split
import time
import os
from gservices import gspread_service


def twitter(links):
    twitters = list(filter(has_twitter, links))
    if len(twitters) > 0:
        username = twitters[0]['username']
        if username.startswith('@'):
            return username[1:]
        else:
            return username
    return None


def twitch(links):
    twitchs = list(filter(has_twitch, links))
    if len(twitchs) > 0:
        return twitchs[0]['username']
    return None


def has_twitter(link):
    if 'platform' in link and link['platform'] == 'twitter':
        return True
    return False


def has_twitch(link):
    if 'platform' in link and link['platform'] == 'twitch':
        return True
    return False


def store_links(links):
    channel_ids_ranges = fetch_channel_ids_cells()["values"]
    twitter_username_rows = []
    twitter_link_rows = []
    twitch_username_rows = []
    twitch_link_rows = []
    for channel_id_rows in channel_ids_ranges:
        link = find_link(links, channel_id_rows[0])
        if link is not None:
            if 'twitter_username' in link and link['twitter_username'] is not None:
                twitter_username_rows.append([
                    f'@{link["twitter_username"]}',
                ])
                twitter_link_rows.append([
                    f'=hyperlink("https://twitter.com/{link["twitter_username"]}"; "LINK")',
                ])
            else:
                twitter_username_rows.append([
                    '',
                ])
                twitter_link_rows.append([
                    '',
                ])
            if 'twitch_username' in link and link['twitch_username'] is not None:
                twitch_username_rows.append([
                    f'@{link["twitch_username"]}',
                ])
                twitch_link_rows.append([
                    f'=hyperlink("https://twitch.tv/{link["twitch_username"]}"; "LINK")',
                ])
            else:
                twitch_username_rows.append([
                    '',
                ])
                twitch_link_rows.append([
                    '',
                ])
        else:
            twitter_username_rows.append([
                '',
            ])
            twitter_link_rows.append([
                '',
            ])
            twitch_username_rows.append([
                '',
            ])
            twitch_link_rows.append([
                '',
            ])
    data = [
        {
            "range": "W3:W",
            'values': twitter_username_rows,
        },
        {
            "range": "AB3:AB",
            'values': twitter_link_rows,
        },
        {
            "range": "Q3:Q",
            'values': twitch_username_rows,
        },
        {
            "range": "U3:U",
            'values': twitch_link_rows,
        }
    ]
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': data,
    }
    return gspread_service().spreadsheets().values().batchUpdate(
        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
        body=body,
    ).execute()


def find_link(links, channel_id):
    for link in links:
        if link["youtube_channel_id"] == channel_id:
            return link
    return None


if __name__ == '__main__':
    load_dotenv()
    channel_ids = fetch_channel_ids()
    requests = split(channel_ids, 50)
    links = []
    for request in requests:
        fetched = fetch_channel_depths(request)
        for item in fetched:
            links.append({
                "youtube_channel_id": item['youtube_channel_id'],
                "twitter_username": twitter(item['links']),
                "twitch_username": twitch(item['links'])
            })
        time.sleep(1)
    print(links)
    store_links(links)
