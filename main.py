from dotenv import load_dotenv
from utils import split
from links import remove_handler
from twitch import fetch_twitch_usernames, fetch_users, store_twitch_channels, fetch_followers_count_batch, store_followers_counts
from tiktok import fetch_tiktok_usernames, store_tiktok_channels
from tiktok_ext import fetch_tiktok_channels
from twitter import fetch_twitter_usernames, fetch_twitter_user, store_twitter_users
from multiprocessing import Pool
import time


def main():
    load_dotenv()
    # Fetch & store data related to YouTube
    start = time.time()
    pool = Pool()
    # Fetch & store data related to Twitch
    twitch_usernames = list(map(remove_handler, fetch_twitch_usernames()))
    twitch_usernames_slices = split(twitch_usernames, 100)
    users = []
    for slice in twitch_usernames_slices:
        fetched = fetch_users(slice)
        users.extend(fetched['data'])
    print(store_twitch_channels(users))
    # Fetch & store data related to Twitch followers count
    twitch_user_ids = list(map(lambda user: user['id'], users))
    twitch_users_slices = split(twitch_user_ids, 50)
    followers_counts = []
    for slice in twitch_users_slices:
        fetched = fetch_followers_count_batch(slice, pool)
        followers_counts.extend(fetched)
    print(store_followers_counts(followers_counts))
    # Fetch & store data related to TikTok
    tiktok_channels = []
    for slice in fetch_tiktok_channels(fetch_tiktok_usernames(), pool):
        tiktok_channels.append(slice)
    print(store_tiktok_channels(tiktok_channels))
    # Fetch & store data related to Twitter
    guest_token = None
    twitter_users = []
    for username in fetch_twitter_usernames():
        data, guest_token = fetch_twitter_user(username[1:], guest_token)
        twitter_users.append(data)
    twitter_users = [user for user in twitter_users if user is not None]
    print(store_twitter_users(twitter_users))
    pool.close()
    pool.join()
    end = time.time()
    print(f"Time taken: {end - start} seconds")


if __name__ == '__main__':
    main()
