from dotenv import load_dotenv
from youtube import fetch_channel_ids, fetch_channels, store_channels
from youtube_ext import fetch_channel_depths
from links import store_links
from utils import split
from links import twitter, twitch, tiktok, remove_handler
from twitch import fetch_twitch_usernames, fetch_users, store_twitch_channels, fetch_followers_count_batch, store_followers_counts
from tiktok import fetch_tiktok_usernames, store_tiktok_channels
from tiktok_ext import fetch_tiktok_channels
from multiprocessing import Pool
import time


def main():
    load_dotenv()
    # Fetch & store data related to YouTube
    start = time.time()
    channel_ids = fetch_channel_ids()
    youtube_ids_slices = split(channel_ids, 50)
    youtube_channels = []
    with Pool() as p:
        responses = p.map(fetch_channels, youtube_ids_slices)
        p.close()
        p.join()
    for response in responses:
        youtube_channels.extend(response['items'])
    print(store_channels(youtube_channels))
    # Fetch & store data related to other platforms
    links = []
    for item in fetch_channel_depths(channel_ids):
        links.append({
            "youtube_channel_id": item['youtube_channel_id'],
            "twitter_username": twitter(item['links']),
            "twitch_username": twitch(item['links']),
            "tiktok_username": tiktok(item['links'])
        })    
    print(store_links(links))
    # Fetch & store data related to Twitch
    twitch_usernames = list(map(remove_handler, fetch_twitch_usernames()))
    twitch_usernames_slices = split(twitch_usernames, 100)
    users = []
    with Pool() as p:
        responses = p.map(fetch_users, twitch_usernames_slices)
        p.close()
        p.join()
    for response in responses:
        users.extend(response['data'])
    print(store_twitch_channels(users))
    # Fetch & store data related to Twitch followers count
    twitch_user_ids = list(map(lambda user: user['id'], users))
    twitch_users_slices = split(twitch_user_ids, 50)
    followers_counts = []
    for slice in twitch_users_slices:
        fetched = fetch_followers_count_batch(slice)
        followers_counts.extend(fetched)
    print(store_followers_counts(followers_counts))
    # Fetch & store data related to TikTok
    tiktok_channels = []
    for slice in fetch_tiktok_channels(fetch_tiktok_usernames()):
        tiktok_channels.append(slice)
    print(store_tiktok_channels(tiktok_channels))
    end = time.time()
    print(f"Time taken: {end - start} seconds")


if __name__ == '__main__':
    main()
