from dotenv import load_dotenv
from youtube import fetch_channel_ids, fetch_channels, store_channels
from youtube_ext import fetch_channel_depths
from links import store_links
from utils import split
from links import twitter, twitch
import time


def main():
    load_dotenv()
    # Fetch & store data related to YouTube
    channel_ids = fetch_channel_ids() 
    youtube_ids_slices = split(channel_ids, 50)
    channels = []
    for slice in youtube_ids_slices:
        fetched = fetch_channels(slice)['items']
        channels.extend(fetched)
    store_channels(channels)
    # Fetch & store data related to other platforms
    links = []
    for slice in youtube_ids_slices:
        fetched = fetch_channel_depths(slice)
        for item in fetched:
            links.append({
                "youtube_channel_id": item['youtube_channel_id'],
                "twitter_username": twitter(item['links']),
                "twitch_username": twitch(item['links'])
            })
        time.sleep(1)
    store_links(links)


if __name__ == '__main__':
    main()
