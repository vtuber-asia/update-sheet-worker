from dotenv import load_dotenv
from youtube import fetch_channel_ids, fetch_channels, store_channels
from youtube_ext import fetch_channel_depths
from links import store_links
from utils import split
from links import twitter, twitch, tiktok, remove_handler
from twitch import fetch_twitch_usernames, fetch_users, store_twitch_channels, fetch_followers_count_batch, store_followers_counts
from tiktok import fetch_tiktok_usernames, store_tiktok_channels
from tiktok_ext import fetch_tiktok_channels
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
    print(store_channels(channels))
    # Fetch & store data related to other platforms
    links = []
    for slice in youtube_ids_slices:
        fetched = fetch_channel_depths(slice)
        for item in fetched:
            links.append({
                "youtube_channel_id": item['youtube_channel_id'],
                "twitter_username": twitter(item['links']),
                "twitch_username": twitch(item['links']),
                "tiktok_username": tiktok(item['links'])
            })
        time.sleep(1)
    print(store_links(links))
    # Fetch & store data related to Twitch
    twitch_usernames_slices = split(fetch_twitch_usernames(), 100)
    users = []
    for slice in twitch_usernames_slices:
        fetched = fetch_users(list(map(remove_handler, slice)))
        users.extend(fetched['data'])
        print(fetched)
    print(store_twitch_channels(users))
    # Fetch & store data related to Twitch followers count
    twitch_users_slices = split(users, 50)
    followers_counts = []
    for slice in twitch_users_slices:
        fetched = fetch_followers_count_batch(list(map(lambda user: user['id'], slice)))
        followers_counts.extend(fetched)
        time.sleep(1)
    print(store_followers_counts(followers_counts))
    # Fetch & store data related to TikTok
    tiktok_username_slices = split(fetch_tiktok_usernames(), 50)
    tiktok_channels = []
    for slice in tiktok_username_slices:
        fetched = fetch_tiktok_channels(slice)
        tiktok_channels.extend(fetched)
        time.sleep(1)
    print(store_tiktok_channels(tiktok_channels))


if __name__ == '__main__':
    main()
