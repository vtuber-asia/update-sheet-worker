from dotenv import load_dotenv
from youtube import fetch_channel_ids, fetch_channels, store_channels
from utils import split
from links import twitter


def main():
    load_dotenv()
    channel_ids = fetch_channel_ids()
    requests = split(channel_ids, 50)
    channels = []
    for request in requests:
        fetched = fetch_channels(request)['items']
        channels.extend(fetched)
    store_channels(channels)


if __name__ == '__main__':
    main()
